#!/usr/bin/env python3
"""Videshi Writer — 4 fresh NEWS articles for 2026-05-22 (afternoon batch 2)
Focus: Immigration crackdown, H-1B, diaspora politics, Sikh representation
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase config ──
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

def sb_patch(table, filters, data):
    r = requests.patch(f"{SB_URL}/rest/v1/{table}?{filters}", headers={**HEADERS, "Prefer": "return=minimal"}, json=data, timeout=30)
    return r.status_code

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Green Card AOS Restriction
# Topic: 95d38ce2-37a0-46c9-bca9-73b9cee5278d (score 86)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "95d38ce2-37a0-46c9-bca9-73b9cee5278d",
    "headline": "The Trump Administration Just Killed Adjustment of Status. For 600,000 Indians Waiting for Green Cards, the Lifeline Is Gone.",
    "subheadline": "A USCIS policy memo issued Friday reclassifies in-country green card applications as 'extraordinary relief,' forcing most temporary visa holders — including H-1B workers, students, and their families — to leave the United States and apply from consulates abroad.",
    "slug": make_slug("trump-kills-adjustment-of-status-indian-green-card"),
    "category": "nri-world",
    "vertical": "immigration",
    "diaspora_angle": "For the estimated 600,000 Indians in the green card backlog — many of whom have lived, worked, and raised children in America for a decade or more — the end of Adjustment of Status is not a policy change. It is an eviction notice dressed in legalese.",
    "tags": ["immigration", "green card", "adjustment of status", "USCIS", "H-1B", "Indian diaspora", "consular processing", "Trump administration"],
    "urgency": "breaking",
    "sources": json.dumps([
        {"name": "Reuters — USCIS tells foreigners seeking green cards: Return to your countries to apply", "url": "https://www.reuters.com/legal/government/uscis-tells-foreigners-seeking-green-cards-return-your-countries-apply-2026-05-22/"},
        {"name": "CNN — Trump admin now requiring green card seekers to leave US to apply", "url": "https://www.cnn.com/2026/05/22/politics/green-card-seekers-leave-us-apply"},
        {"name": "Wall Street Journal — Trump Administration to Make Green Card Applicants File Overseas", "url": "https://www.wsj.com"},
        {"name": "LatestLY — New US Green Card Rules: Temporary Visa Holders Must Return Home", "url": "https://www.latestly.com/us/new-us-green-card-rules-temporary-visa-holders-must-return-to-their-home-country-to-apply-7442724.html"},
        {"name": "Fox News — Trump administration orders green card applicants to leave the US", "url": "https://foxnews.com/politics/trump-administration-orders-green-card-applicants-leave-us-apply-home-countries"}
    ]),
    "score_total": 92,
    "status": "published",
    "published_at": now,
    "body": """The U.S. government announced on Friday what may be the single most consequential immigration policy change affecting Indian professionals in a generation. In a policy memo issued by U.S. Citizenship and Immigration Services, the Trump administration has effectively ended the routine use of Adjustment of Status — the process that allowed temporary visa holders already living in the United States to apply for green cards without leaving the country.

Under the new guidance, USCIS has reclassified Adjustment of Status as an "extraordinary form of relief," meaning approvals will now be granted only in limited and exceptional circumstances — victims of violent crimes, human trafficking survivors, and other humanitarian cases. Everyone else, including the hundreds of thousands of H-1B workers, international students, and their family members who previously relied on AOS, must now return to their home countries and apply for permanent residency through consular processing at American embassies abroad.

"An alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply," the Department of Homeland Security wrote on X. "This policy allows our immigration system to function as the law intended instead of incentivizing loopholes. The era of abusing our nation's immigration system is over."

## What Adjustment of Status Actually Was

To understand what was lost, you need to understand what AOS provided. For decades, it was the mechanism that allowed a software engineer in Sunnyvale on an H-1B visa — whose employer had filed a green card petition on her behalf — to continue living, working, and raising her children in America while the application wound through the system. She could change jobs (using EAD work authorization), her spouse could work, and her children could attend school without interruption.

The alternative — consular processing — requires the applicant to physically travel to a U.S. consulate in their home country, attend an interview, submit biometrics, and wait for visa issuance. For applicants with clean cases and short backlogs, this can be completed in weeks. For Indian applicants in the employment-based EB-2 and EB-3 categories, where the backlog stretches decades, the calculus is entirely different.

An Indian H-1B worker who has been in the United States for twelve years, whose children were born in America, whose mortgage is in California, and whose green card priority date is still years from becoming current, now faces a binary choice: leave the country she has built a life in and apply from a consulate in Chennai or Delhi, or remain and hope her case qualifies as "extraordinary."

## The Scale of the Impact

The numbers are staggering. According to USCIS data, there are approximately 1.1 million pending employment-based green card applications, and Indians account for roughly 60-70 per cent of that backlog — a function of the per-country cap that limits each nation to 7 per cent of annual green cards regardless of demand. Some Indian applicants filed their initial labour certifications in 2012 and are still waiting.

Under the old system, these applicants could file I-485 Adjustment of Status applications once their priority dates became current (or close to current under certain provisions), allowing them to remain in the U.S. with work authorisation while waiting. That safety net is now gone for most applicants.

The policy also affects international students on F-1 visas who transition to H-1B status and eventually seek green cards, spouses on H-4 dependent visas, and L-1 intracompany transferees — collectively, a population that numbers in the hundreds of thousands and is overwhelmingly South Asian.

## The Consular Processing Bottleneck

The administration's directive to route most green card applications through consular processing assumes that the State Department's consular infrastructure can handle the volume. Immigration attorneys are deeply sceptical.

U.S. consulates in India — particularly in Mumbai, Chennai, Hyderabad, and New Delhi — already face appointment backlogs of months for routine visa interviews. Adding hundreds of thousands of green card applicants to that queue would create processing times that could stretch years, during which applicants would be in limbo: unable to work in the U.S., unable to maintain their American lives, and unable to return until their cases are adjudicated.

For families with American-born children, the disruption is acute. A child born in Houston to Indian parents on H-1B visas is a U.S. citizen by birth. If those parents must now leave the country to apply for their green cards, the family faces months or years of separation — or the child must be uprooted from their school, their friends, and the only country they have ever known.

## The Legal Battle Ahead

Immigration lawyers expect immediate legal challenges. The American Immigration Lawyers Association and several advocacy groups have signalled that the policy memo may exceed USCIS's statutory authority, since Adjustment of Status is codified in the Immigration and Nationality Act as a right available to eligible applicants, not a discretionary favour.

The legal argument centres on Section 245 of the INA, which provides that an alien "may apply to the Attorney General for adjustment of his or her status to that of an alien lawfully admitted for permanent residence." The word "may" has historically been interpreted as conferring a right to apply, with the government retaining discretion over approval — not over whether the application can be filed at all.

The administration's counter-argument, articulated by USCIS spokesperson Zach Kahler, is that it is "returning to the original intent of the law" and that AOS was always meant to be exceptional. "We're returning to the original intent of the law to ensure aliens navigate our nation's immigration system properly," Kahler said. Legal scholars on both sides are preparing for a fight that will likely reach federal courts within weeks.

## What This Means for Indian Families Tonight

For the Indian diaspora, the policy lands at a moment of compounding anxiety. The $100,000 H-1B fee imposed last September has already reduced new registrations. Tech layoffs have pushed thousands of H-1B workers into 60-day grace periods. And now, the pathway from temporary work visa to permanent residency — the arc that has defined Indian immigration to America for three decades — has been fundamentally disrupted.

The WhatsApp groups are already on fire. Immigration attorneys in the Bay Area report being flooded with calls. The question everyone is asking is the one that no policy memo can answer: if America does not want us to stay, where exactly are we supposed to go?

The administration would say: home. For people who have spent a decade or more building lives in the United States, the word has lost its geographic meaning.""",
    "word_count": 1050,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: H-1B Registrations Drop 38.5%
# Topic: 05139f9f-1c02-48fe-b83a-81146d61e925 (score 84)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "05139f9f-1c02-48fe-b83a-81146d61e925",
    "headline": "H-1B Registrations Plummet 38.5 Per Cent to Decade-Low Levels. The $100,000 Fee Did Exactly What It Was Designed to Do.",
    "subheadline": "USCIS data shows FY2027 registrations fell from 344,000 to 212,000. The administration calls it a triumph over 'low-wage abuse.' For the Indian tech pipeline that supplies 71 per cent of all H-1B approvals, it is an existential contraction.",
    "slug": make_slug("h1b-registrations-plummet-38-percent-decade-low-100k-fee"),
    "category": "nri-world",
    "vertical": "immigration",
    "diaspora_angle": "Indians account for 71 per cent of all H-1B approvals. A 38.5 per cent drop in registrations means tens of thousands fewer Indians will enter the American tech workforce this year — and the ripple effects reach every engineering college in Hyderabad, Pune, and Chennai that has built its placement narrative around the American dream.",
    "tags": ["H-1B", "visa", "USCIS", "immigration", "Indian workers", "tech", "Trump", "100K fee"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Swadesi — H-1B Registrations Drop 38.5% in FY27", "url": "https://swadesi.com/news/h-1b-registrations-down-in-fy27-more-approvals-for-higher-degrees-sala-mpgyrm6b"},
        {"name": "The Local Report — H-1B registrations fell 38.5% in FY2027", "url": "https://articles.thelocalreport.in"},
        {"name": "Storyboard18 — 60 days or leave? US tech layoffs put Indian H-1B workers under pressure", "url": "https://www.storyboard18.com/how-it-works/60-days-or-leave-us-tech-layoffs-put-indian-h-1b-workers-under-pressure-98850.htm"},
        {"name": "TechWord News — H-1B visa registrations saw a 38% drop", "url": "https://techwordnews.com"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "body": """The numbers are in, and they tell the story that the Trump administration wanted to tell. H-1B visa registrations for fiscal year 2027 plummeted by 38.5 per cent, falling from 343,981 in FY2026 to just 211,600 — a level that immigration attorneys say mirrors the registration volumes of a decade ago, before the programme became the primary conduit for Indian tech talent into the American workforce.

USCIS announced the data on Thursday in a post on X, framing the decline as evidence that the programme is "better serving its intended purpose of attracting highly skilled foreign workers and protecting the wages, working conditions, and job opportunities of American workers."

The agency was not subtle about what it considers progress. "The days of abusing the programme with mass, low-wage registrations are over," USCIS said. Only 17.7 per cent of selected registrations were in the lowest wage category, down from significantly higher proportions in recent years. Nearly three-quarters of approved applicants — 71.5 per cent — held a U.S. master's degree or higher, compared to 57 per cent last year.

## The $100,000 Wall

The single largest driver of the decline is the fee. On September 19, 2025, President Trump signed a proclamation restricting the entry of H-1B workers whose petitions are not accompanied by a $100,000 payment. The fee — technically a "supplemental registration fee" — applies to petitions filed by companies whose workforce composition does not meet certain thresholds of American workers.

In practice, the fee has functioned as a filter. Large Indian IT services companies — Infosys, TCS, Wipro, HCL, and their peers — historically filed thousands of H-1B petitions annually for workers deployed to client sites across America. These were often at Level I and Level II wage categories, which the administration characterised as below-market. The $100,000 fee made bulk filings at those wage levels economically unviable.

The result is visible in the data. The companies that relied on volume — filing hundreds or thousands of petitions in each lottery cycle — have dramatically reduced their participation. The companies that remain are those filing for individually critical hires at higher salary bands: Google, Microsoft, Amazon, Meta, and the tier of employers for whom $100,000 per petition is a rounding error on a $300,000 total compensation package.

## What the Shift Looks Like

The composition of the H-1B pool has changed as dramatically as its size. USCIS highlighted that an "overwhelming" 71.5 per cent of selected registrations were for workers holding a U.S. master's degree or higher. This is the advanced-degree cap exemption at work: applicants with master's degrees from American universities get an additional lottery chance, and employers filing for them tend to be direct-hire companies rather than staffing firms.

The policy has, in effect, bifurcated the Indian talent pipeline into two tiers. Tier one: graduates of American universities — IIT alumni who went to Stanford, NIT graduates who studied at Georgia Tech, engineers who earned master's degrees at UT Austin — who are being hired directly by top-tier companies at salaries above $130,000. This group is seeing higher selection rates than ever before. Tier two: experienced professionals in India being recruited by IT services firms for deployment to the U.S. — the backbone of the Indian outsourcing industry's American operations. This group has been largely priced out.

## The Ripple Effect in India

The consequences extend far beyond American immigration offices. The Indian IT services industry — a $250 billion sector that employs over five million people — has built its business model on the ability to deploy skilled workers to client sites in the United States. The H-1B visa was the mechanism that made that model work. With registrations down 38.5 per cent and the economics of bulk petitioning destroyed, the industry faces a structural shift.

TCS, Infosys, and Wipro have already been increasing their American hiring — recruiting U.S. residents and green card holders rather than flying in workers from Bengaluru. But this transition is expensive, slower than visa-based deployment, and erodes the cost advantage that made Indian IT services globally competitive in the first place.

For the engineering colleges that feed the pipeline — the regional institutions in Hyderabad, Pune, Chennai, and Coimbatore that built placement records on the promise of American deployments — the decline represents a fundamental challenge to their value proposition. When a parent investing ₹15 lakh in a computer science degree asks "will my child get to go to America?", the honest answer has shifted from "probably" to "only if they get into a top American graduate programme first."

## The Immigration Squeeze Tightens

The H-1B decline does not exist in isolation. It arrives on the same day that USCIS announced the effective end of Adjustment of Status for most green card applicants, requiring temporary visa holders to leave the United States to apply for permanent residency. Combined, these two policies represent a coordinated constriction of the Indian professional immigration pipeline at both ends: fewer new workers coming in, and a harder path to permanence for those already here.

For the roughly 600,000 Indians currently in the U.S. on various temporary work visas and their dependents, the message from Washington is increasingly legible: you are welcome to work here temporarily, at high wages, in roles that American employers certify they cannot fill domestically. But the era of mass Indian immigration to America through the tech corridor — the great migration that transformed the demographics of Sunnyvale, Edison, and Frisco — is being deliberately curtailed.

Mark Krikorian, Executive Director of the Center for Immigration Studies and a long-time critic of the H-1B programme, was characteristically blunt in his assessment: "These changes are all good, in the sense of being less bad — but only the real solution is to abolish the H-1B programme altogether."

For the 71 per cent of H-1B approvals that carry Indian names, the question is no longer whether the rules are changing. It is whether the change is temporary or permanent — and whether the American dream that drew them still exists in recognisable form.""",
    "word_count": 960,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: Nancy Mace vs Krishnamoorthi — Naturalized Citizens Ban
# Topic: 524fb2aa-5600-4d6d-af26-7c0720b41cb1 (score 83)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "524fb2aa-5600-4d6d-af26-7c0720b41cb1",
    "headline": "A Republican Congresswoman Wants to Ban Naturalized Citizens From Holding Federal Office. Raja Krishnamoorthi Took It Personally.",
    "subheadline": "Nancy Mace's proposed constitutional amendment would bar immigrants who became citizens from serving in Congress, on the federal bench, or in Senate-confirmed positions. The Indian-American congressman born in New Delhi called it 'bigotry and hate.'",
    "slug": make_slug("nancy-mace-ban-naturalized-citizens-federal-office-krishnamoorthi"),
    "category": "nri-world",
    "vertical": "politics",
    "diaspora_angle": "For the 4.4 million Indian-Americans in the United States — a community that includes naturalized citizens serving in Congress, the federal judiciary, and senior government roles — the Mace amendment is not a legislative curiosity. It is a direct statement about whether immigrants who become citizens are considered fully American.",
    "tags": ["Nancy Mace", "Raja Krishnamoorthi", "naturalized citizens", "Congress", "constitutional amendment", "Indian Americans", "immigration", "Pramila Jayapal", "Ilhan Omar"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "American Bazaar — Krishnamoorthi rebukes proposal restricting naturalized citizens from federal office", "url": "https://americanbazaaronline.com/2026/05/21/krishnamoorthi-rebukes-proposal-restricting-naturalized-citizens-from-federal-office-481306/"},
        {"name": "Devdiscourse — US lawmaker moves amendment to ban foreign-born congressmen, judges", "url": "https://www.devdiscourse.com"},
        {"name": "India Weekly — Nancy Mace Proposal on Naturalized Citizens Sparks Backlash", "url": "https://indiaweekly.biz"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "body": """Representative Nancy Mace, Republican of South Carolina, proposed a constitutional amendment this week that would require all members of Congress, federal judges, and Senate-confirmed officers of the United States to be natural-born citizens. The proposal would expand the constitutional eligibility restriction that currently applies only to the president and vice president, extending it to every significant federal office in the country.

For Raja Krishnamoorthi — the Indian-American congressman from Illinois who arrived in the United States from New Delhi as an infant — the proposal was not an abstraction. It was a description of a country in which he, specifically, would be barred from serving.

"My parents came to America seeking a better life," Krishnamoorthi wrote on X in response to the proposal. He called the amendment "morally wrong" and urged colleagues to reject what he described as "bigotry and hate."

## The Proposal

Mace's amendment would expand the "natural-born citizen" requirement enshrined in Article II of the Constitution — which governs presidential eligibility — to cover House members, senators, federal judges, and all Senate-confirmed government officials. Under current law, members of Congress must meet age, residency, and citizenship-duration requirements, but there is no bar on naturalized citizens serving.

In announcing the proposal, Mace publicly referenced three Democratic lawmakers: Ilhan Omar of Minnesota, born in Somalia; Pramila Jayapal of Washington, born in India; and Shri Thanedar of Michigan, born in India. All three are naturalized U.S. citizens. Critics immediately noted that Mace did not reference any Republican members of Congress who are also naturalized citizens, framing the proposal as partisan targeting dressed in constitutional language.

Jayapal responded by calling the proposal "hateful" in a public statement. "This amendment is un-American in the most literal sense — it would create a permanent underclass of citizens who did everything right, took the oath, passed the test, and are told they are still not good enough," she said.

## The Constitutional Reality

The proposal faces nearly insurmountable procedural barriers. A constitutional amendment requires approval by two-thirds of both the House and Senate, followed by ratification by 38 of the 50 state legislatures. In the current political environment, achieving that level of bipartisan consensus on any immigration-related measure — let alone one that would strip rights from existing citizens — is effectively impossible.

Constitutional scholars were quick to point out the irony: the Founders deliberately chose to restrict the natural-born requirement to the presidency, leaving Congress open to naturalized citizens. Alexander Hamilton, himself born in the British West Indies, served as the nation's first Treasury Secretary. The 14th Amendment, ratified in 1868, explicitly guarantees equal protection under the law to all citizens, making no distinction between those born on American soil and those who chose to become American.

## Why It Matters to the Indian Diaspora

The Mace proposal may never become law, but its symbolic weight is significant — and for the Indian-American community, the timing is particularly charged.

Indian-Americans have achieved remarkable representation in American public life over the past decade. Kamala Harris served as vice president. Vivek Ramaswamy ran for president. Kash Patel serves as FBI Director. Sriram Krishnan advises the White House on AI policy. Pramila Jayapal chairs the Congressional Progressive Caucus. Shri Thanedar represents Detroit. Raja Krishnamoorthi was, until recently, one of the most prominent Indian-American voices in the House.

Many of these individuals are naturalized citizens or the children of immigrants. The Mace amendment, if it were ever enacted, would retroactively disqualify a significant number of the Indian-Americans who have reached the highest levels of federal service.

The proposal also lands in a political environment where Indian-Americans are being courted by both parties. The Republican Party has made significant inroads with Hindu-American voters in recent cycles, emphasising shared values on entrepreneurship, education, and national security. A constitutional amendment that would bar naturalized Indian-Americans from federal office cuts directly against that outreach — a tension that has not gone unnoticed in community organisations from Houston to Edison.

## The Broader Pattern

The Mace amendment does not exist in isolation. It is the latest in a series of proposals from Republican lawmakers that immigration advocates describe as a systematic narrowing of the rights and protections available to immigrants, even those who have become citizens.

The Randy Fine Act, proposed in the House, would ban dual citizenship for sitting members of Congress. The Trump administration's restrictions on Adjustment of Status, announced the same week, force green card applicants to leave the country. The $100,000 H-1B fee has reduced visa registrations by 38.5 per cent. Taken individually, each measure has its own policy rationale. Taken together, they describe a trajectory.

For naturalized citizens — people who stood in a government office, renounced foreign allegiances, and swore an oath to the United States Constitution — the Mace proposal asks a question they thought they had already answered: are you really one of us?

The amendment requires two-thirds of Congress and 38 states to find out. It will almost certainly not get there. But the fact that the question was asked, publicly, by a sitting member of Congress, is itself an answer of a different kind.""",
    "word_count": 850,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 4: Dr Gunisha Kaur — First Sikh on USCIRF
# Topic: a007ca04-de7f-407c-b23e-04776bf66b65 (score 83)
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": "a007ca04-de7f-407c-b23e-04776bf66b65",
    "headline": "Dr. Gunisha Kaur Just Became the First Sikh to Serve on America's Religious Freedom Commission. Her Appointment Is Bigger Than Symbolism.",
    "subheadline": "Appointed by Senator Chuck Schumer to the U.S. Commission on International Religious Freedom, the anesthesiologist and human rights researcher will monitor persecution in the countries where Sikh communities face the greatest threats — including India, Afghanistan, and Iran.",
    "slug": make_slug("gunisha-kaur-first-sikh-uscirf-religious-freedom-commission"),
    "category": "nri-world",
    "vertical": "politics",
    "diaspora_angle": "For the 700,000 Sikhs in America and millions more worldwide, the appointment puts a Sikh voice inside the only U.S. government body whose sole mandate is investigating religious persecution abroad — at a time when transnational repression targeting Sikh activists has become a diplomatic flashpoint between India, the U.S., and Canada.",
    "tags": ["Gunisha Kaur", "USCIRF", "Sikh", "Chuck Schumer", "religious freedom", "human rights", "Sikh Coalition", "India", "transnational repression"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "American Bazaar — Dr. Gunisha Kaur appointed to USCIRF by Senator Chuck Schumer", "url": "https://americanbazaaronline.com/2026/05/21/dr-gunisha-kaur-appointed-to-uscirf-by-senator-chuck-schumer-481317/"},
        {"name": "Senator Chuck Schumer — Official Press Release", "url": "https://www.schumer.senate.gov"},
        {"name": "Sikh Coalition — USCIRF appointment announcement", "url": "https://www.sikhcoalition.org"},
        {"name": "Global Indian News Network — Indian-origin Gunisha Kaur nominated to US panel", "url": "https://globalindiannewsnetwork.com"},
        {"name": "Simranjeet Singh Substack — Dr. Gunisha Kaur: Appointed a Federal Commissioner", "url": "https://simranjeetsingh.substack.com"}
    ]),
    "score_total": 79,
    "status": "published",
    "published_at": now,
    "body": """Senator Chuck Schumer announced this week that Dr. Gunisha Kaur has been appointed to the U.S. Commission on International Religious Freedom, making her the first Sikh to serve on the bipartisan body that monitors religious persecution worldwide and advises Congress, the President, and the Secretary of State on policy responses.

The appointment is historic in the most literal sense — in the 28 years since USCIRF was established under the International Religious Freedom Act of 1998, no Sikh has ever served as a commissioner. But its significance extends well beyond the milestone. Kaur's arrival on the commission comes at a moment when the issues most central to Sikh communities globally — transnational repression, religious persecution in South Asia, and the targeting of activists and dissidents by foreign intelligence services — are also among the most sensitive in American foreign policy.

## Who She Is

Kaur is not a political appointee in the traditional mould. She is a practising anesthesiologist who serves as Director of the Weill Cornell Medicine Human Rights Impact Lab — a research programme that investigates the health consequences of persecution, displacement, and state-sponsored violence. She holds board positions at Ensaaf, a human rights organisation focused on impunity for mass violence in Punjab, and is a Stephen M. Kellen Term Member at the Council on Foreign Relations.

Her academic work sits at the intersection of medicine and human rights documentation — the kind of expertise that USCIRF was designed to draw on but has often lacked. The commission's mandate includes conducting fact-finding missions abroad, reviewing State Department designations of "Countries of Particular Concern" for severe religious freedom violations, and producing annual reports that serve as the primary congressional reference on global persecution.

"Dr. Kaur will make history as the first and only Sikh to serve on the commission, and I am honoured to support a commissioner with such extensive experience in human rights and community leadership," Schumer said. "I am confident that she will bring her deep medical, academic, research, and leadership expertise to her service on the commission."

## Why It Matters Now

The timing of the appointment is not incidental. Over the past three years, transnational repression targeting Sikh activists in the West has become one of the most consequential diplomatic issues between India, the United States, and Canada.

The 2023 assassination of Hardeep Singh Nijjar on Canadian soil — later attributed by Canadian intelligence to agents linked to the Indian government — triggered a diplomatic crisis between Ottawa and New Delhi that has yet to fully resolve. In the United States, federal prosecutors indicted an Indian government operative in connection with an alleged plot to assassinate Sikh separatist leader Gurpatwant Singh Pannun on American soil. India has denied the allegations but acknowledged the existence of a parallel investigation.

USCIRF has already engaged with these issues. The commission has raised concerns about the targeting of Sikh human rights defenders, and the Sikh Coalition — which advocated for Kaur's appointment — has worked closely with USCIRF to document cases of transnational repression.

Kaur's appointment ensures that these concerns will have an institutional advocate inside the commission, one with the academic credentials and research infrastructure to move beyond anecdotal reporting and produce the kind of systematic documentation that influences policy.

## The Broader Landscape

India currently appears on USCIRF's watch list — a classification one step below the "Country of Particular Concern" designation reserved for the world's worst violators. The commission has previously recommended that India be elevated to CPC status, citing concerns about the Citizenship Amendment Act, restrictions on religious minorities in several states, and the use of anti-conversion laws to target Christians and Muslims.

For the Indian government, having a Sikh human rights researcher on USCIRF is unlikely to be welcome news. New Delhi has consistently rejected the commission's assessments as politically motivated and has declined to grant USCIRF delegations access to India for fact-finding visits.

For the Sikh-American community, the calculus is different. Harman Singh, Executive Director of the Sikh Coalition, framed the appointment in terms of the community's own history. "Sikh history is deeply tied to issues central to the mission of USCIRF, including persecution, displacement, and the defence of fundamental human rights," he said. He noted that challenges to religious freedom in South Asia and humanitarian crises affecting Sikh communities in Iran and Afghanistan make Sikh representation "especially important."

## What a Commissioner Can Actually Do

USCIRF commissioners serve two-year terms and operate in an advisory capacity — they cannot impose sanctions, issue visas, or direct foreign policy. But the commission's influence is not negligible. Its annual reports set the terms of congressional debate on religious freedom. Its CPC recommendations trigger statutory requirements for the State Department to respond. And its fact-finding missions produce findings that are cited by courts, legislators, and international bodies.

Kaur's specific expertise — documenting the health impacts of persecution and state violence — could shift the commission's analytical approach. USCIRF reports have traditionally focused on legal frameworks, individual cases, and policy recommendations. A commissioner who brings medical and epidemiological methodology to the assessment of persecution can produce a different kind of evidence — one that quantifies harm rather than merely cataloguing it.

For the estimated 700,000 Sikhs in America and the 25 million Sikh community worldwide, the appointment represents something that has been missing for nearly three decades: a seat at the table where the United States decides which persecutions to name, which governments to pressure, and which communities to protect.""",
    "word_count": 880,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# INSERT ALL ARTICLES + MARK TOPICS
# ══════════════════════════════════════════════════════════════

print(f"Publishing {len(articles)} articles...")
success = 0
for i, article in enumerate(articles):
    topic_id = article.get("topic_id")
    try:
        result = sb_post("p2_articles", article)
        if isinstance(result, list) and len(result) > 0:
            print(f"  ✅ [{article['category']}] {article['headline'][:80]}...")
            success += 1
            if topic_id:
                sb_patch("p2_topics", f"id=eq.{topic_id}", {"status": "published", "updated_at": now})
                print(f"     Topic {topic_id[:8]} → published")
        elif isinstance(result, dict) and result.get("id"):
            print(f"  ✅ [{article['category']}] {article['headline'][:80]}...")
            success += 1
            if topic_id:
                sb_patch("p2_topics", f"id=eq.{topic_id}", {"status": "published", "updated_at": now})
                print(f"     Topic {topic_id[:8]} → published")
        else:
            print(f"  ⚠️  [{article['category']}] Response: {json.dumps(result)[:200]}")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ [{article['category']}] Error: {e}")
        print(f"     Response: {e.response.text[:300]}")
    except Exception as e:
        print(f"  ❌ [{article['category']}] Error: {e}")

# Mark overlapping/duplicate topics as covered
overlap_topics = [
    # UK Net Migration Halves — same topic as already-published UK migration articles
    "f3e2fe9e-d885-4943-b953-e06f56b22616",
    "1f1e1b8a-7a9f-4e2b-bab4-1a99da006792",
    # H-1B 60-day grace period — covered within H-1B/AOS articles above
    "08e5289c-0318-43c9-9ea4-fac61e6931f3",
    # UK Anti-Hindu Hate Monitor — already published in previous batch
    "5141eb92-fcb4-4140-9a6d-bf31362a9114",
]
for tid in overlap_topics:
    sb_patch("p2_topics", f"id=eq.{tid}", {"status": "published", "updated_at": now})
    print(f"  📌 Overlap topic {tid[:8]} → published")

print(f"\nDone: {success}/{len(articles)} articles published.")
