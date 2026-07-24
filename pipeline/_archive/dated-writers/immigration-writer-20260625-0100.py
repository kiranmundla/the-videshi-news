#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
env_file = Path.home() / ".env.supabase"
if not env_file.exists():
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Citizenship Was Supposed to Be the Finish Line. The Government Is Reopening 250 Cases",
        "subheadline": "The Justice Department aims to file at least 250 denaturalization suits by October — a 25-fold jump over the recent norm. For Indian Americans who saw the passport as the end of the immigration ordeal, the ground just shifted.",
        "slug": make_slug("doj-denaturalization-surge-250-cases-naturalized-citizens-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest groups of naturalized Americans, so a sweeping denaturalization drive turns what felt like a settled status back into something that can be litigated — and that anxiety reaches even citizens who did everything by the book.",
        "tags": ["denaturalization", "citizenship", "doj", "naturalization", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN — Trump administration ramps up effort to revoke citizenship", "url": "https://www.cnn.com/2026/06/19/politics/denaturalization-citizenship-trump"},
            {"name": "Greenville News (USA TODAY Network) — Denaturalization expansion", "url": "https://www.greenvilleonline.com/story/news/2026/06/24/trump-denaturalization-expansion/"},
            {"name": "Statesman Journal — Federal government seeks to strip citizenship", "url": "https://www.statesmanjournal.com/story/news/2026/06/17/federal-government-denaturalization-oregon/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/16029871/pexels-photo-16029871.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A man holds an American flag in Washington, D.C., where the Justice Department is expanding its denaturalization caseload",
        "image_attribution": "Pexels",
        "body": """For most of the people who carry one, a U.S. passport is the document that ends the conversation. The interviews are over, the oath is taken, the file is closed. The Justice Department is now reopening some of those files.

According to a senior department official, the government plans to file at least 250 denaturalization cases by October — civil suits seeking to strip naturalized Americans of their citizenship. In under two months this year it has already filed 29. To grasp how far this departs from the norm: between 2008 and June 2026, the entire federal system filed 166 such complaints, an average of fewer than ten a year. The Biden administration filed 24 in four years. The new target represents roughly a 25-fold acceleration.

## What is actually changing

Denaturalization is not new, and it is not, on its face, lawless. It is a civil tool Congress has kept on the books for decades, used historically against war criminals and people who lied about terrorism ties. What has changed is volume and intent. A June 2025 memo from Assistant Attorney General Brett Shumate instructed the Civil Division to "prioritize and maximally pursue" these cases, and laid out ten categories — national-security risks, war crimes, fraud during the naturalization process, and undisclosed felonies among them. Crucially, the memo says the list does not limit which cases the division can pursue.

A 12-attorney denaturalization unit is now working a backlog and fielding referrals from the Department of Homeland Security. Because the cases are labor-intensive, the department is pulling civil-fraud litigators and front-office appointees to expand capacity, and routing cases to U.S. attorney offices that may file "several hundred more."

## Why Indian Americans should read the fine print

Indians are among the largest sources of new U.S. citizens. Nearly eight million people naturalized in the past decade, and the Indian diaspora — over six million strong, by India's own count — is heavily represented in that figure. The categories the government cites, particularly "fraud" and "material misrepresentation" during naturalization, are broad enough to unsettle people who believe their cases were clean.

That is the quiet cost here. Denaturalization is a civil proceeding, which means there is no right to a government-appointed lawyer and the burden of proof is lower than in a criminal trial. A decades-old paperwork discrepancy — an address, an employment detail, a question answered imprecisely on a form filed years ago — becomes, in theory, something a litigator can build a case around. For a community that treated naturalization as the moment immigration stress finally ended, that is a meaningful psychological shift.

## The practical takeaways

For the overwhelming majority of naturalized Indian Americans, nothing about their daily life changes, and panic is unwarranted. The cases announced so far involve serious alleged conduct — terrorism support, war crimes, undisclosed criminal histories. But the diaspora's lawyers are offering consistent, sober advice worth repeating:

- **Keep your naturalization file.** Retain the N-400 application, interview notes, and any supporting documents. Consistency between what you filed then and what you say now is the best protection.
- **Disclose accurately, always.** Any future immigration filing — sponsoring a relative, for instance — should not contradict earlier statements.
- **Treat a notice seriously.** A denaturalization complaint is a lawsuit. It is answered in federal court, not at a USCIS window, and it warrants a lawyer immediately.

The broader signal matters as much as the individual cases. Citizenship has long been described as the most secure status in American immigration law. The administration's own framing — that it is "a privilege" that can be "forfeited" — recasts it as something more conditional. For a diaspora that has built families, businesses and retirements on the assumption of permanence, the message lands even when the lawsuit never comes."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Judge Just Pulled the Plug on a Database That Was Flagging Naturalized Citizens as Non-Voters",
        "subheadline": "A federal court vacated the revamped SAVE system, warning it threatened to purge eligible voters. Internal memos admitted naturalized citizens were the most likely to be wrongly flagged — a group that includes hundreds of thousands of Indian Americans.",
        "slug": make_slug("save-database-voter-purge-blocked-naturalized-citizens-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Naturalized Indian Americans are precisely the voters a citizenship-verification database is most likely to misflag, so a ruling that halts bulk voter checks is a direct, if quiet, protection for the diaspora's right to vote.",
        "tags": ["voting", "save-database", "naturalized-citizens", "dhs", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "New York Post — Judge blocks Trump admin from using federal database", "url": "https://nypost.com/2026/06/23/us-news/judge-blocks-trump-admin-from-using-federal-database-to-check-citizenship/"},
            {"name": "Reuters — Judge blocks use of revamped immigration database for voter checks", "url": "https://www.reuters.com/legal/judge-blocks-trump-immigration-database-voter-checks-2026-06-23/"},
            {"name": "Democracy Docket — Federal judge blocks DHS from using citizenship database", "url": "https://www.democracydocket.com/news/judge-blocks-dhs-save-database-voter-purge/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7103185/pexels-photo-7103185.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A voter holds a ballot; a federal court halted a database used to screen voter rolls for citizenship",
        "image_attribution": "Pexels",
        "body": """The story of naturalized Americans being told they are not citizens usually plays out one frightened person at a time, at a DMV counter or in a rejection letter. This week it played out across a 75-page federal court opinion that named the problem directly — and, for now, stopped it.

U.S. District Judge Sparkle L. Sooknanan vacated the Trump administration's revamped version of SAVE — the Systematic Alien Verification for Entitlements system — ruling that the government had "knowingly trampled on the privacy rights of American citizens in a manner that threatens the sacred right to vote." It is a technical ruling with a very practical consequence for the diaspora.

## What SAVE became

SAVE was built to let agencies check whether someone qualifies for a public benefit. After a March 2025 executive order on election "integrity," DHS rebuilt it into something much larger. The agency added natural-born citizens to the register, plugged in direct access to Social Security Administration records, and — most consequentially — allowed states to run **bulk searches** using names, birthdays and Social Security numbers rather than individualized, DHS-issued ID numbers.

States then began comparing their voter rolls against this database and canceling the registrations of people flagged as non-citizens. The trouble, as voting-rights groups argued and the judge accepted, is that the data is often outdated. Someone who naturalized recently can still appear in the system under an old, non-citizen status — and get swept off the rolls despite being fully eligible to vote.

## The detail that matters for the diaspora

The most striking line in Judge Sooknanan's opinion was not hers. She cited **internal DHS memos** that themselves warned naturalized citizens would be "at particular risk of having their registrations erroneously cancelled." In other words, the government's own analysts flagged the flaw before the system went live.

That is the heart of why this is a diaspora story. Indian Americans are one of the fastest-growing naturalized populations in the country, with hundreds of thousands taking the oath in recent years. By definition, they are the people most likely to sit in the gap between an old database entry and a current legal status. A naturalized engineer in Texas or a physician in Ohio who voted without incident for years could, under a bulk SAVE search, be flagged as a suspected non-citizen and forced to prove their citizenship to stay registered.

The judge declined to rule on the constitutional questions — whether the executive branch can run national voter verification at all — and rested her decision on narrower statutory grounds: the Privacy Act and the Computer Matching and Privacy Protection Act of 1988, laws Congress passed precisely to stop the government from building centralized data banks on citizens. She also noted the administration is now 0-9 in related lawsuits seeking complete state voter rolls.

## What it means in practice

For naturalized Indian Americans, the ruling is a reprieve, not a resolution:

- **Your registration is safer for now.** The bulk-search mechanism that drove erroneous cancellations is paused.
- **Check your status anyway.** Voters who naturalized recently should confirm their registration is active well before any election, since some states already acted on SAVE data before the ruling.
- **Keep your naturalization certificate accessible.** If a state challenges your status, the certificate is the cleanest proof.

The administration reacted bitterly, with a DHS lawyer calling the decision an obstacle to "addressing alien voting." But the case is a reminder of a structural truth the diaspora rarely thinks about until it bites: in a system that increasingly cross-checks citizenship by algorithm, the people most likely to be wrongly caught are exactly those who earned their citizenship most recently — and worked hardest for it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Doctors' Carve-Out: Why Indian Physicians Won a Quieter Battle Over the $100,000 H-1B Fee",
        "subheadline": "Indian American physician groups are celebrating a court ruling that blocked the $100,000 H-1B charge from hitting doctors — a fight with stakes that run straight through America's rural and safety-net hospitals.",
        "slug": make_slug("aapi-physicians-h1b-100k-fee-blocked-img-indian-doctors-rural"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian-origin doctors are a backbone of U.S. medicine — one in four American physicians is an international medical graduate — so a fee that priced them out of H-1B sponsorship would have hit Indian American families and the underserved patients they treat at the same time.",
        "tags": ["h1b", "physicians", "aapi", "img", "healthcare", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — AAPI Applauds Court Ruling Blocking $100,000 H-1B Physician Visa Requirement", "url": "https://www.theindianeye.com/aapi-applauds-court-ruling-blocking-100000-h1b-physician-visa-requirement/"},
            {"name": "South Asian Herald — AAPI Welcomes Court Ruling", "url": "https://southasianherald.com/aapi-welcomes-court-ruling-blocking-100000-h1b-visa-requirement-for-physicians/"},
            {"name": "USA Today — How Trump's immigration policies hurt legal immigration", "url": "https://www.usatoday.com/story/news/nation/2026/06/24/trump-immigration-policies-legal-immigration-data/"}
        ]),
        "score_total": 74,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6129452/pexels-photo-6129452.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A physician in a hospital; international medical graduates make up about one in four U.S. doctors",
        "image_attribution": "Pexels",
        "body": """When a Massachusetts federal judge struck down the Trump administration's $100,000 H-1B fee this month, the headlines belonged to the tech industry. But a second constituency had been holding its breath, and it is one the diaspora knows well: doctors.

The American Association of Physicians of Indian Origin (AAPI), one of the largest ethnic medical organizations in the country, welcomed the ruling as "a healthcare victory." Its president, Dr. Amit Chakrabarty, framed it bluntly: the decision, he said, "restores fairness and stability to a system that thousands of international physicians depend upon." Behind the careful language is a real fear about what a six-figure visa fee would have done to the way medicine is staffed in America's least glamorous corners.

## Why a tech-visa fee threatened hospitals

The H-1B is usually discussed as a Silicon Valley instrument. It is also how a large share of foreign-trained doctors enter and remain in the U.S. workforce. International medical graduates — physicians trained outside the U.S. and Canada — make up roughly **25% of practicing American doctors**, and Indian-origin physicians are the single largest national group within that cohort.

These doctors are not evenly distributed. They concentrate disproportionately in rural hospitals, safety-net institutions and underserved communities — the places that struggle to recruit U.S.-trained graduates. A $100,000 charge per petition, AAPI argued, would not have been absorbed quietly. Cash-strapped rural hospitals would have rescinded job offers rather than pay it, leaving vacancies unfilled in precisely the regions that can least afford a doctor shortage.

"Many hospitals would have struggled to absorb such a financial burden," Dr. Chakrabarty said. "The consequences would have been immediate — fewer physicians, longer wait times, and reduced access to care."

## The diaspora dimension

For Indian American families, this is personal in two directions at once. There is the physician on an H-1B — frequently completing a residency or working under a J-1 waiver in a designated shortage area — whose career path runs through exactly the visa the fee would have taxed. And there are the patients, many of them in small towns far from any Indian enclave, who would have felt the loss of those doctors first.

The medical community's relief, though, is tempered. The ruling invalidated the fee on the narrow ground that the administration imposed it without congressional authorization — calling it an unlawful "tax" rather than a regulatory fee. It did not resolve the underlying push to make the H-1B harder and costlier. Diaspora policy advocates have warned that the administration retains other levers: procedural hurdles, heightened scrutiny of petitions, and the broader consular-processing and adjustment-of-status changes already reshaping the green-card path. The administration is also expected to appeal.

## What physicians should watch

For Indian-origin doctors and the institutions that hire them, the practical guidance is to treat the win as a pause, not a peace:

- **The fee is blocked, not buried.** An appeal could revive the question, and the legal fight may run through multiple circuits.
- **J-1 waiver timelines still bite.** Physicians moving from a J-1 waiver into H-1B status face their own deadlines and should not assume the broader visa environment has eased.
- **Sponsorship math is shifting.** Even without the $100,000 charge, rising premium-processing and petition costs are changing how hospitals budget for international hires.

The larger point is one the diaspora's doctors have made for years and rarely get credit for: immigration policy aimed at "the H-1B" does not stop at the technology sector. It runs through emergency rooms and rural clinics, and the people on both ends of the stethoscope — physician and patient alike — are often the ones who feel a Washington fee schedule first."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\nTotal inserted: {len(inserted)}/{len(articles)}")
for h in inserted:
    print(f"  - {h}")
