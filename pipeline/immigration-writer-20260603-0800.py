#!/usr/bin/env python3
"""
Immigration writer — 2026-06-03 08:00 UTC
Two articles: (1) AOS policy walkback + Pew data, (2) $100K fee numbers analysis
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

# --- ARTICLE 1: AOS Walkback + Pew Data ---

article1_body = """The Trump administration spent the last week of May telling hundreds of thousands of green card applicants to pack their bags. Then, over the weekend, it told everyone to calm down.

On May 22, USCIS issued a policy memo directing immigration officers to steer adjustment-of-status applicants — people already living and working in the United States on temporary visas — toward consular processing in their home countries instead. The language was blunt: anyone "in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

The backlash was immediate. Immigration attorneys flooded social media with warnings. Business groups called it reckless. Lawmakers from both parties questioned the legality of restricting a pathway written into federal statute by Congress. Within days, the Department of Homeland Security issued a clarification: this was merely a "reminder to officers of their discretionary authority," not a blanket policy change.

That might have settled things — if USCIS adjudicators weren't already sending out new Requests for Evidence asking applicants to prove their circumstances are "extraordinary." CNN obtained one such RFE listing a dozen factors officers could weigh: hardship to the applicant's family, evidence of community service, English proficiency. The policy may not have changed on paper, but something has clearly shifted in practice.

## The Numbers That Matter

Fresh data from the Pew Research Center, published on June 2, puts the stakes in sharp relief. In fiscal year 2024, 58 percent of all green cards issued in the United States went to people who adjusted their status from within the country — 782,770 people in total. Only 42 percent were processed through consulates abroad.

For Indian nationals, the picture is even more skewed. Sixty-one percent of Indians who received green cards in FY2024 did so through adjustment of status — some 39,190 people. Among all employment-based green card recipients, the AOS share was 69 percent. These are not people gaming the system. They are H-1B holders whose employers filed immigrant petitions, whose priority dates finally became current after years — sometimes decades — of waiting.

Forcing them to leave the country and apply from abroad means entering a consular processing pipeline where Indian interview wait times already stretch 10 to 12 months. It means losing H-4 EAD work authorization for spouses during that wait. It means children who age out of dependent status while stuck in administrative processing abroad. For anyone whose case hits a "221(g) administrative hold" at the consulate — a common occurrence for Indian applicants — the delay can extend indefinitely.

## The Legal Reality

Immigration attorneys remain cautiously optimistic that the policy won't survive legal scrutiny. "I bet you there's a million pending adjustment applications," Atlanta-based immigration attorney Charles Kuck told CNN. "You cannot say now to those million people, 'Thanks for your money, I need you to go to your home country and restart this all over again.' No judge upholds that."

Kuck pointed out that adjustment of status exists in a statute created by Congress, not an administrative regulation that can be unilaterally rewritten. "When Congress amends and betters a law 20 times, it's hard to call that a loophole," he said.

Rep. Grace Meng, chair of the Congressional Asian Pacific American Caucus, was less diplomatic: "This new policy will rip apart families, spouses, and children from their parents."

## What This Means for Indian Americans

The timing is particularly cruel for the Indian diaspora. EB-2 India's final action date is already frozen until October. The PERM labor certification backlog sits at 503 days. The H-1B system just imposed a $100,000 fee. And now the one stable step in the green card journey — filing I-485 from within the US while continuing to work — is being treated as a privilege rather than a right.

For the approximately 400,000 Indians currently in the employment-based green card backlog, the message from the administration has been consistent: every pathway will be made harder, every timeline longer, every cost higher. The walkback of the AOS memo doesn't change the direction. It just adds confusion to the cruelty."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "Sixty-One Percent of Indian Green Cards Just Became 'Discretionary'",
    "subheadline": "Pew Research data quantifies the damage as USCIS walks back — then quietly implements — its adjustment-of-status crackdown.",
    "slug": make_slug("indian-green-card-aos-pew-data-discretionary-walkback"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "61% of Indian immigrants received green cards through adjustment of status in FY2024. The USCIS memo threatens to force tens of thousands of Indian H-1B holders — already trapped in multi-decade backlogs — to leave the country and apply from consulates with 10-12 month wait times, risking family separation and job loss.",
    "tags": ["green-card", "adjustment-of-status", "uscis", "pew-research", "h1b", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Pew Research Center", "url": "https://www.pewresearch.org/short-reads/2026/06/02/majority-of-new-green-cards-have-gone-to-immigrants-already-living-in-us/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/31/politics/trump-green-card-messaging-confusion-anxiety/index.html"},
        {"name": "NBC Palm Springs / AP", "url": "https://www.nbcpalmsprings.com/2026/05/22/trump-administration-orders-green-card-applicants-to-leave-us"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/trump-administration-seeks-to-downplay-impact-of-green-card-policy-changes-report/article71047689.ece"},
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/24/chair-meng-condemns-reckless-green-card-policy-change/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg",
    "is_editorial": False,
    "body": article1_body.strip()
}

# --- ARTICLE 2: $100K Fee Numbers Analysis ---

article2_body = """In his first Senate budget hearing as DHS Secretary, Markwayne Mullin casually dropped a number that should have stopped the room cold: of the 286,000 H-1B applications received in fiscal year 2026, more than 200,000 applicants paid the $100,000 fee.

Do the arithmetic. That is at least $20 billion flowing into federal coffers from a single visa category in a single year. It is also a confession: the fee has not reduced H-1B applications. It has stratified them.

Applicants who pay $100,000 get their cases processed in roughly 15 days. Everyone else waits 7.5 months. What was sold as a deterrent has become a toll road — and nearly 70 percent of applicants have decided the toll is worth paying.

## Who Can Afford It and Who Cannot

For a Google or a Meta filing on behalf of a senior engineer, $100,000 is a rounding error on the cost of a Silicon Valley hire. The company pays the fee, absorbs it into headcount budgets, and moves on. The worker arrives in two weeks.

But Senator Susan Collins of Maine described a different reality during the hearing. A hospital in Presque Isle — a rural community in northern Maine with no other options — recently paid $100,000 to bring in a surgeon from overseas. "I would suggest that there's a huge difference between bringing in a computer expert from another country to work in wealthy California and Silicon Valley versus a much-needed surgeon to work at a rural hospital in northern Maine," Collins told Mullin.

Alaska's Lisa Murkowski flagged the same problem for teachers. School districts in remote parts of her state depend on H-1B educators to fill positions that American graduates simply will not take. For a rural school district operating on a budget measured in the low millions, a $100,000 visa fee is not a cost of doing business. It is a dealbreaker.

"We're really anxious about this as school districts are looking to bring on and hire more of our teachers," Murkowski told Mullin, promising to follow up with specific proposals.

## The Indian Dimension

Indians account for roughly three-quarters of all H-1B approvals. They are the visa's dominant constituency and, by extension, its primary targets. For a mid-career software engineer whose employer is willing to sponsor an H-1B, the $100,000 fee is typically employer-borne — uncomfortable but manageable. For Indian doctors being recruited to staff hospitals in rural Mississippi or Indian teachers filling shortages in tribal schools, the economics collapse entirely.

The fee also creates perverse downstream effects. Indian IT consulting firms — already under scrutiny for their H-1B usage — face the choice of passing the cost to clients, absorbing it and watching margins evaporate, or simply reducing US hiring. Several have already signaled they will shift work offshore, precisely the outcome the fee was ostensibly designed to prevent.

## The Two-Tier System Is Now Official

Mullin, to his credit, acknowledged the problem. "We do have some authority and flexibility to be able to waive some of this on a case by case," he told Collins. He said DHS was open to reviewing proposals: "We're happy to look into it, look at language, try to get it better."

This represents a meaningful softening from the administration's initial position that the fee was non-negotiable. But case-by-case waivers are not a system. They are a pressure-release valve that benefits applicants with political connections and well-funded lobbyists — not the Presque Isle hospital administrator trying to keep a surgeon on staff.

What Mullin's numbers actually reveal is that the United States has built, perhaps inadvertently, a two-tier immigration processing system. Tier one: pay $100,000, get processed in 15 days, carry on with your life. Tier two: wait 7.5 months in limbo, unable to start work, unable to plan, hoping nothing goes wrong with your petition while the clock runs.

For Indian professionals navigating an immigration system that already includes multi-decade green card backlogs, a wage-weighted H-1B lottery, and a $250 visa integrity fee from the reconciliation bill, the $100,000 premium is less a fee than a ransom. And the 200,000 who paid it this year are proof that when the alternative is 7.5 months of uncertainty, people will pay almost anything to make it stop."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Two Hundred Thousand Paid. Eighty-Six Thousand Didn't. The H-1B's New Class Divide.",
    "subheadline": "DHS Secretary Mullin revealed that 70% of H-1B applicants paid $100,000 for 15-day processing. The numbers expose a two-tier system where rural hospitals and Indian teachers are priced out.",
    "slug": make_slug("h1b-100k-fee-200000-paid-two-tier-class-divide"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indians make up ~75% of H-1B approvals and bear the brunt of the $100K fee. While Big Tech absorbs the cost, Indian doctors staffing rural hospitals and Indian teachers filling school shortages face an impossible calculus — as do IT consulting firms whose business models depend on H-1B hiring.",
    "tags": ["h1b", "100k-fee", "uscis", "dhs", "mullin", "rural-healthcare", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Hindu BusinessLine / PTI", "url": "https://www.thehindubusinessline.com/news/over-2-lakh-applicants-paid-100000-for-h-1b-visas-says-dhs-secretary-mullin/article71055322.ece"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100-000-h-1b-visa-fees"},
        {"name": "IANS", "url": "https://ianslive.in/news/us-lawmakers-seek-h1b-relief-for-foreign-teachers-20260603"},
        {"name": "Inshorts", "url": "https://inshorts.com/en/news/over-2-lakh-paid-100000-for-faster-processing-of-h1b-visas-us"}
    ]),
    "score_total": 82,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "is_editorial": False,
    "body": article2_body.strip()
}

# --- INSERT ---

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
