#!/usr/bin/env python3
"""Immigration writer — 2026-07-07 13:00 PDT run. Three articles."""

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


# ──────────────────────────────────────────
# ARTICLE 1: Ohio Judge Blocks Nationality Bias
# ──────────────────────────────────────────
art1_body = """A federal judge in Columbus, Ohio, has issued a preliminary injunction blocking two USCIS policies that immigration attorneys have been quietly warning about for months: the indefinite pausing of benefit applications for people from certain countries, and the use of an applicant's nationality as "a significant negative factor" in deciding those applications.

U.S. District Judge Algenon Marbley's July 6 ruling sided with 25 immigrants already living lawfully in the United States — citizens of Burma, Canada, Iran, Nigeria, Syria, Tanzania and Venezuela. Among them: a hospital pharmacist, a registered nurse, a cancer researcher, a university professor, and several engineers. All had pending applications for work authorisation or lawful permanent residency. All had watched those applications stall.

## What USCIS Was Doing

The challenged policies expanded presidential proclamations that restricted entry from certain countries into something broader. USCIS was not just screening new arrivals — it was pausing benefit applications for people already here, people who had been working legally for years.

The agency argued this fell within its discretion under the broader umbrella of the president's entry restrictions. Judge Marbley disagreed. In a 69-page opinion, he wrote that USCIS had exceeded its authority under the Administrative Procedure Act and immigration law by extending travel bans into the domestic benefits adjudication process.

"The question is whether USCIS has the legal authority to enact its Challenged Policies in the first place, which is a purely legal question that this Court is well-equipped to address," Marbley wrote.

He also rejected the government's claim that national security concerns placed the policies beyond judicial review.

## The Political Context

Marbley — nominated by President Bill Clinton in 1997 — devoted a significant portion of his opinion to public statements by President Trump and Vice President JD Vance, including Vance's widely publicised false claims about Haitian immigrants in Springfield, Ohio. He also cited Governor Mike DeWine's public dismissal of those allegations and the bomb threats they provoked against schools, a hospital, and city government in Springfield.

But Marbley stressed these statements were "important but not essential" to his legal conclusion. The ruling rests on statutory and administrative law grounds, not on claims of political animus.

## What This Means for Indian Americans

The 25 plaintiffs are not Indian nationals. But the policy mechanism they challenged — treating nationality as a negative factor in benefit adjudications — is a precedent that could be applied to any nationality, including India.

India accounts for roughly 41 per cent of all pending employment-based I-485 applications. Hundreds of thousands of Indian nationals hold H-1B extensions, H-4 EADs, and other benefits that require periodic USCIS adjudication. If the agency were to expand its nationality-based slowdown to include Indian applicants — or if it already has, informally — this ruling establishes that courts will intervene.

Immigration attorneys have reported anecdotal delays in Indian applicants' cases that go beyond the expected processing backlogs. Whether those delays are a symptom of this exact policy or simply the weight of oversubscribed categories remains unclear. But the legal principle is now on the record: USCIS cannot treat where you were born as a reason to delay or deny your application.

## The Limit

The injunction is preliminary and applies only to the 25 named plaintiffs. It does not block the policies nationwide — a limitation that has taken on new significance after the Supreme Court's separate ruling this week curbing federal courts' ability to issue nationwide injunctions.

The case continues. But for now, a federal judge has told the government something that should have been obvious: if you are already here legally, your application should be judged on its merits, not your passport."""


# ──────────────────────────────────────────
# ARTICLE 2: Day 1 CPT Under Threat
# ──────────────────────────────────────────
art2_body = """There is a quiet, widespread practice among Indian tech workers in the United States that almost nobody talks about openly: when you lose the H-1B lottery — again — you enrol in another master's degree programme. Not because you want a second degree, but because Day 1 Curricular Practical Training lets you keep working legally while you wait for another shot at the lottery.

That escape hatch is about to close.

## The Proposed Rule

On May 5, the Department of Homeland Security proposed eliminating the "Duration of Status" framework that has governed F-1 student visas for decades. Under the current system, international students can remain in the US as long as they maintain their student status. No fixed end date, no periodic renewal through USCIS.

The proposed rule would replace this with a fixed admission period of up to four years. Any extension — including those needed for continuing studies or post-graduation work authorisation — would require formal approval from USCIS, not just a sign-off from the university's international student office.

The grace period after a student's status ends would also shrink from 60 days to 30 days.

## Why Day 1 CPT Dies

Day 1 CPT programmes exist because of Duration of Status. The logic works like this: you have a master's degree, you cannot get an H-1B, so you enrol in a second master's programme at a university that offers CPT from the first day of classes. Your student status keeps you legal. CPT lets you keep working. The university handles the paperwork.

Under the proposed rule, that entire chain breaks. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" said Danielle Goldman, co-founder and CEO of Build, an immigration technology platform.

USCIS would now gate every extension. And the agency has made its position on Day 1 CPT abundantly clear: it views the practice as a loophole, not a pathway.

## The Scale of the Problem

Indian nationals dominate both sides of this equation. They are the largest group of international students in the US, and they account for a disproportionate share of H-1B lottery applicants. With the lottery now weighted by salary rather than random selection — a change effective since February 2026 — entry-level and mid-career Indian workers at outsourcing firms face even worse odds.

Thousands of Indian professionals in AI, machine learning, software engineering, and data science currently rely on Day 1 CPT as their only legal option to remain employed in the United States. Goldman estimates the impact extends to "a substantial portion of the US AI talent pool."

The F-1 rejection rate for Indian applicants hit 61 per cent last year. OPT fraud investigations are ongoing across multiple fronts. And now the backup to the backup is being dismantled.

## What Employers Face

The loss of Day 1 CPT does not just affect workers. American companies that depend on these workers face a talent pipeline problem they cannot solve by hiring domestically.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," Goldman said. "The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions."

Those alternatives — cap-exempt H-1B programmes at universities and research institutions, O-1 visas for extraordinary ability, EB-1A self-petitions — are real, but they serve a fraction of the population currently relying on Day 1 CPT.

## The Diaspora Calculation

For Indian families who have spent years building careers, buying homes, and raising American-born children, the Day 1 CPT pathway was never glamorous. Nobody celebrates enrolling in a degree they do not need. But it was legal, it worked, and it kept families intact.

Goldman's advice to international students: develop multiple backup plans rather than relying solely on H-1B lottery selection or Day 1 CPT programmes.

The problem is that for many, Day 1 CPT was the backup plan. And when the backup plan disappears, the only option left is the one nobody wants to talk about: leaving."""


# ──────────────────────────────────────────
# ARTICLE 3: SCOTUS Ends Nationwide Injunctions
# ──────────────────────────────────────────
art3_body = """For the better part of two years, a single federal judge in a single courtroom could stop the entire federal government from enforcing an immigration policy. A nationwide injunction — a judicial order blocking a policy not just for the plaintiffs in the case, but everywhere — was the most powerful tool immigration advocates had.

On Monday, the Supreme Court took it away.

## What the Court Did

In a 6-3 decision, the Court ruled that federal judges can no longer issue orders that block government policies across the entire country. Injunctions must now be limited to the parties before the court — the specific people or organisations that filed the lawsuit.

During President Trump's second term alone, lower courts have issued more than 40 nationwide injunctions to block various immigration policies, from the birthright citizenship executive order to the $100,000 H-1B fee to the elimination of Duration of Status. Each of those injunctions protected millions of people who never set foot in a courtroom.

That protection structure has been dismantled.

## How It Worked Before

When a federal judge in Washington state blocked Trump's executive order on birthright citizenship in January 2025, the order applied everywhere. A baby born in Texas was protected by a ruling in Seattle. An H-1B worker in New Jersey benefited from a judge's order in California.

This made strategic sense for advocacy groups. File one well-crafted lawsuit in a favourable jurisdiction, get one judge to agree, and the entire policy freezes while the case works through the appeals process. It was efficient. It was also, conservatives argued, an abuse of judicial power that allowed individual judges to act as national policymakers.

## What Changes Now

An immigration attorney in Ohio who wins a case blocking a USCIS policy now wins it only for their specific clients. The same policy continues to apply to everyone else in the country.

This creates several immediate consequences for Indian Americans.

**The H-1B fee litigation fractures.** Three federal circuits have issued conflicting rulings on the $100,000 H-1B fee. Without nationwide injunctions, the fee could be blocked in some circuits and enforced in others, creating a patchwork where your employer's location determines whether you pay $100,000 or nothing.

**Green card processing policies vary by jurisdiction.** USCIS policies that are blocked in one district — like the nationality-based benefit delays just struck down in Ohio — remain fully operative everywhere else.

**Class action becomes the only path to broad relief.** Attorneys must now file Rule 23 class actions to protect groups of similarly situated immigrants, a far more resource-intensive process than seeking a single nationwide injunction.

## The Birthright Citizenship Connection

The immediate trigger for this ruling was the ongoing battle over Trump's birthright citizenship executive order. The Court's June 30 decision upheld the 14th Amendment principle that children born on US soil are citizens regardless of their parents' status.

But Monday's ruling on injunctions partially undercuts that victory. Immigration attorney Alex Galvez warned that without nationwide injunctions, the executive order could take effect in states where no one files for a local block. "In Texas, the children that are born there after 30 days, they might be born without any birth certificate if there's no injunction," he said.

States like California, where the attorney general has challenged the order, would still have protections. Other states might not. Congressman Raul Ruiz warned that the decision "opens up the possibility that different states will offer different rights, disintegrating the idea that we are one nation."

## What Indian Families Should Know

Indian Americans have been indirect beneficiaries of nationwide injunctions more than almost any other immigrant group. The H-1B fee block, the processing time standards, the DACA protections — these court-ordered guardrails shielded millions of Indians who never joined a lawsuit.

Going forward, legal advocacy will need to be more localised, more expensive, and more individually targeted. Immigration law firms that previously relied on a single favourable ruling will now need to file independent challenges in multiple jurisdictions.

For an Indian engineer in Dallas whose green card application has stalled, a court victory in Columbus, Ohio, no longer helps. She would need her own lawsuit, her own attorney, and her own judge.

The Supreme Court has not changed immigration law. It has changed who gets to benefit from the courts that interpret it. And for a community that has relied on those courts to push back against an increasingly hostile administrative state, the math just got significantly worse."""


# ──────────────────────────────────────────
# Assemble & Insert
# ──────────────────────────────────────────
articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Federal Judge Just Told USCIS It Cannot Punish People for Where They Were Born",
        "subheadline": "An Ohio court ruled that the agency overstepped by delaying benefit applications and using nationality as a negative factor — a decision that could ripple well beyond the 25 plaintiffs who brought the case.",
        "slug": make_slug("federal-judge-blocks-uscis-nationality-bias-ohio-immigration"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India accounts for 41% of pending employment-based green card applications — if USCIS applies nationality-based slowdowns to Indians, this Ohio ruling establishes the legal precedent that courts will intervene.",
        "tags": ["uscis", "immigration", "court-ruling", "nationality-bias", "green-card", "h1b"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Columbus Dispatch", "url": "https://www.dispatch.com/story/news/courts/2026/07/06/trump-uscis-immigration-benefits-policy-blocked-by-federal-judge-in-ohio/90823065007/"},
            {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/stricter-vetting-slower-processing-how-new-immigration-form-changes-are--pracin-2026-07-06/"},
            {"name": "NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Close-up of an open passport with various immigration stamps",
        "image_attribution": "Pexels",
        "body": art1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Day 1 CPT Safety Net Is Fraying. Thousands of Indian Tech Workers Have No Plan B",
        "subheadline": "A proposed DHS rule would eliminate Duration of Status for student visas, effectively killing the re-enrolment pathway that has kept H-1B lottery losers working legally in the US.",
        "slug": make_slug("day-1-cpt-safety-net-closing-indian-tech-workers-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Day 1 CPT is the unofficial backup plan for thousands of Indian tech workers who lose the H-1B lottery — if Duration of Status ends, they face either leaving the US or losing legal work authorization.",
        "tags": ["day-1-cpt", "h1b-lottery", "f1-visa", "duration-of-status", "indian-students", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "IDP Education", "url": "https://www.idp.com/"},
            {"name": "ICEF Monitor", "url": "https://monitor.icef.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&w=1200",
        "image_caption": "Students walking across a university campus on a bright day",
        "image_attribution": "Pexels",
        "body": art2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Supreme Court Just Took Away Immigration's Emergency Brake",
        "subheadline": "A 6-3 ruling bars federal judges from issuing nationwide injunctions — meaning court victories against immigration policies now protect only the people who sued, not everyone else.",
        "slug": make_slug("scotus-ends-nationwide-injunctions-immigration-impact"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian Americans have been indirect beneficiaries of dozens of nationwide injunctions blocking hostile immigration policies — without them, every worker needs their own lawsuit to get the same protection.",
        "tags": ["supreme-court", "nationwide-injunctions", "immigration", "h1b", "green-card", "court-ruling"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "NBC Palm Springs", "url": "https://www.nbcpalmsprings.com/2026/07/07/supreme-court-ruling-paves-way-for-trumps-birthright-citizenship-order/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/"},
            {"name": "Columbus Dispatch", "url": "https://www.dispatch.com/"}
        ]),
        "score_total": 85,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
        "image_caption": "The United States Supreme Court building at dusk in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": art3_body,
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['headline']}")
        print(f"   slug: {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
