#!/usr/bin/env python3
"""Videshi Immigration Writer — 2026-05-29 12:00 UTC run"""
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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Your Green Card Application Just Became a Deportation Risk",
        "subheadline": "A quiet USCIS memo issued on May 21 reframes adjustment of status as 'extraordinary relief,' effectively telling hundreds of thousands of immigrants — including tens of thousands of Indian H-1B holders — to leave the country and apply from abroad.",
        "slug": make_slug("uscis-aos-memo-green-card-leave-country-indian-h1b"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the estimated 700,000+ Indians stuck in the green card backlog, most of whom have been in the US on H-1B visas for a decade or more, this memo transforms what was a routine administrative step into a high-stakes gamble. Leaving the country for consular processing means abandoning jobs, pulling children out of schools, and facing unpredictable wait times at overwhelmed Indian consulates — with no guarantee of approval at the other end.",
        "tags": ["uscis", "green-card", "adjustment-of-status", "h1b", "consular-processing", "immigration-policy"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USA TODAY", "url": "https://www.usatoday.com/story/news/politics/2026/05/27/uscis-green-card-changes-adjustment-of-status/84048837007/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/policy/immigration/3438941/green-card-changes-force-applicants-leave-country/"},
            {"name": "Manifest Law", "url": "https://manifestlaw.com/blog/immigration/news/uscis-policy-memorandum-adjustment-of-status-05-22-2026/"},
            {"name": "PSBP Law", "url": "https://psbplaw.com/new-uscis-adjustment-of-status-memo-explained/"},
            {"name": "Marks Gray", "url": "https://www.marksgray.com/uscis-adjustment-of-status-policy-update/"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32642491/pexels-photo-32642491.jpeg",
        "image_caption": "A US passport and travel documents — the paperwork that now determines whether green card applicants can stay or must leave",
        "body": """On May 21, a week before the Memorial Day weekend, USCIS released Policy Memorandum PM-602-0199. The timing was not subtle. The memo instructs immigration officers to treat adjustment of status — the process by which someone already in the US applies for a green card without leaving — as an "extraordinary" form of relief rather than a standard administrative pathway.

The practical translation: if you are in the United States on a temporary visa and want permanent residency, the government now expects you to go home and apply through a US consulate abroad. Staying and filing from within the country is no longer the default. It is the exception.

## What the Memo Actually Says

The memorandum tells adjudicating officers to weigh the applicant's choice to adjust status inside the US — rather than departing for consular processing — as a *negative factor* in their discretion analysis. Applicants who want to adjust from within the country must demonstrate "unusual or even outstanding equities" to overcome that adverse factor.

Maintaining a dual-intent visa like the H-1B — a category that explicitly contemplates future permanent residence — is "not sufficient, on its own" to warrant approval, according to the memo.

Officers are directed to examine immigration history, status maintenance, any prior violations, fraud concerns, family ties, tax records, and community involvement. Requests for additional evidence tied to the new "extraordinary circumstances" standard have already started arriving at immigration attorneys' offices.

USCIS spokesperson Zach Kahler framed the change as restorative. "We're returning to the original intent of the law to ensure aliens navigate our nation's immigration system properly," he said. "From now on, an alien who is in the US temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances."

## The Scale of Disruption

Roughly one million people become green card holders in the United States each year. According to Department of Homeland Security data, about half of them have historically applied from within the country through adjustment of status. The memo targets this entire population.

Family-based applicants — spouses, parents, and children of US citizens — make up the largest affected group. Employment-based applicants, predominantly H-1B holders, form the second-largest category. Indians account for approximately 71 percent of approved H-1B applications, making them by far the most exposed nationality.

For someone who entered the US as a student fifteen years ago, transitioned to H-1B, married, bought a house, and has children in American schools, "going home to apply" is not a bureaucratic inconvenience. It is an upheaval. Consular processing in India involves unpredictable appointment availability, document requirements that differ from the USCIS process, and the real possibility of denial at a foreign post with limited appeal options.

## What Attorneys Are Saying

Immigration lawyers are urging calm — with caveats. "Adjustment of status has not been eliminated," noted Marks Gray in a client advisory. "Eligible applicants may still file, and USCIS may still approve adjustment applications. However, the new guidance places greater emphasis on the fact that adjustment of status is discretionary."

Manifest Law attorney Ana Gabriela Urizar offered a more measured reading: the memo does not necessarily signal a major shift for properly prepared cases, but "applicants and practitioners may need to place even greater emphasis on presenting the full picture of their positive equities, professional contributions, and long-term value to the United States."

PSBP Law was blunter, calling the memo "yet another attempt to create fear and chaos within the immigration community" despite "decades of USCIS routinely adjudicating and approving adjustment of status applications as a normal part of the legal immigration process."

## The Unanswered Questions

The most consequential ambiguity: does the memo apply to applications already pending, or only to new filings? USCIS has not clarified. For the hundreds of thousands of people with I-485 applications sitting in the backlog — some filed years ago — this silence is not academic. It is the difference between waiting and being told to leave.

The Department of Homeland Security has said the policy does not affect existing green card holders. But for everyone in between — legally present, patiently waiting, deeply rooted — the ground just shifted.

Non-discretionary adjustment pathways for humanitarian categories such as VAWA self-petitioners remain unaffected. But for the vast majority of employment-based and family-based applicants, the memo adds a new variable to an already punishing calculus.

The practical impact will emerge case by case, approval by approval, denial by denial. In the meantime, immigration attorneys are advising clients to strengthen their documentation, maintain lawful status meticulously, avoid international travel, and — above all — not withdraw pending applications."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Kolkata Just Became the Easiest Place in India to Get a US Visa Appointment — If You're Over 50",
        "subheadline": "The US Consulate in Kolkata has launched three pilot programs offering priority visa slots for parents visiting children in America, faster processing for business travelers, and new B1/B2 sub-categories that could reshape how Indians apply for visitor visas.",
        "slug": make_slug("kolkata-us-consulate-b1b2-visa-pilot-parents-priority"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the millions of Indian Americans who spend months — sometimes over a year — trying to get B1/B2 visa appointments for their parents, this pilot directly addresses the most common complaint in the diaspora: 'My parents can't visit me.' If the Kolkata model works and expands to Delhi, Mumbai, Chennai, and Hyderabad, it could transform the parent-visit experience that defines so much of NRI family life.",
        "tags": ["b1-b2-visa", "kolkata-consulate", "parent-visa", "india-us-visa", "business-visa", "visa-appointment"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Air India News", "url": "https://airnews.in/us-consulate-kolkata-new-visa-pilots/"},
            {"name": "TravelOBiz", "url": "https://travelobiz.com/us-consulate-in-kolkata-pilots-3-new-b1-b2-visa-measures-for-applicants/"},
            {"name": "TravelOBiz", "url": "https://travelobiz.com/us-b1-b2-visa-pilot-launched-in-kolkata-shorter-wait-times-likely-for-some-travellers/"},
            {"name": "IMAD Travel", "url": "https://imadtravel.com/us-consulate-kolkata-b1b2-visa-pilot-2026/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7316956/pexels-photo-7316956.jpeg",
        "image_caption": "An American flag on a government building — Kolkata's US Consulate is piloting new visa measures that could reshape how Indians visit the US",
        "body": """The US Consulate General in Kolkata announced three new visa pilot programs on May 21, and for once the news out of an American immigration office is not entirely bleak. The pilots offer priority appointment slots for elderly parents, faster processing for business travelers, and — in the most intriguing development — new sub-categories for B1/B2 visitor visas that have started appearing in the application system.

The consulate framed the initiative as putting "American economic priorities first." In practice, it means that certain categories of Indian applicants in the Kolkata consular district may finally get appointments in weeks rather than months.

## The Parent Track

The headline pilot targets parents aged 50 and above who want to visit their children legally residing in the United States. Eligible applicants must demonstrate a clear and verified travel purpose, established family ties to the US, and strong ties to India — the standard "I'm coming back" assurance that has defined B-visa adjudication for decades.

What changes is the timeline. Instead of competing with the general appointment pool — where wait times at Indian consulates routinely stretch six to twelve months — qualifying parents get priority scheduling.

The criteria are straightforward: be 50 or older, have a child legally in the US, show genuine travel intent. No new visa category is being created, and the approval standard remains identical. A faster appointment does not mean a friendlier interview. But for a 65-year-old mother in Kolkata who wants to see her grandchildren in New Jersey, the difference between a three-month wait and a nine-month wait is not trivial.

## Business Travelers and Tourists

The second pilot creates a separate priority track for business travelers and tourists with established profiles. The consulate's social media announcement specifically mentioned supporting "travellers who strengthen US-India ties."

Likely beneficiaries include frequent business travelers with clean visa histories, attendees of conferences and trade events, individuals with strong financial records and documented travel purposes, and tourists with previous international travel histories. India-US bilateral trade exceeded $190 billion in 2025, and much of that commerce depends on business professionals who need to cross the Pacific regularly. The pilot acknowledges an economic reality that visa backlogs have been quietly undermining.

## The Mystery Sub-Categories

The most interesting — and least confirmed — development involves new B1/B2 sub-categories that some applicants selecting Kolkata as their interview location have started seeing in the online system.

Four categories have been reported: Business Professionals (conditions apply), Parents Visiting Children with Legal Status (conditions apply), General Tourism and Travel (for applicants with no past refusals), and Recent Visa Refusal within 24 months.

The consulate has not officially explained what "conditions apply" means, and the sub-categories have not been formally announced. But their appearance suggests the State Department may be experimenting with triaging applications before the interview stage — routing different applicant profiles through different processing streams based on risk and purpose.

The "Recent Visa Refusal" category is particularly notable. It implies that applicants previously denied within two years are being flagged separately, which could mean either additional scrutiny or, optimistically, a structured path to reapply rather than being thrown back into the general pool.

## What This Means for the Diaspora

Every Indian American knows the visa appointment problem. You want your parents at your child's graduation, your wedding, your new baby's first Diwali. You go to ustraveldocs.com, check availability, and discover the next open slot is eight months away. You refresh obsessively. You join WhatsApp groups that share appointment-cancellation alerts. You consider flying your parents to a third country with shorter wait times.

The Kolkata pilot does not solve this nationwide. It operates at a single consulate, and there is no confirmation it will expand to Delhi, Mumbai, Chennai, or Hyderabad — the four posts that process the vast majority of Indian visa applications. But it establishes a template. If the priority parent track reduces wait times without compromising screening quality, the argument for replication becomes harder to ignore.

The business traveler track matters for a different reason. As remote work and cross-border consulting have grown, so has the population of NRIs and Indian-origin professionals who need to move between countries regularly. Having a dedicated stream for verified business travelers is overdue recognition that not every B1 applicant needs the same level of processing.

## The Caveats

Priority scheduling is not priority approval. Consular officers retain full discretion, and the pilot changes nothing about the 214(b) standard that produces most Indian visa refusals — the presumption that every applicant intends to immigrate unless they prove otherwise.

The social media vetting process introduced by the current administration continues to slow processing across all Indian consulates, and the Kolkata pilot does not exempt applicants from that requirement.

For now, this is one consulate trying something different. Whether it becomes a model or remains an experiment depends on results the State Department has not committed to sharing publicly."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
