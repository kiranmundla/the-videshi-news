#!/usr/bin/env python3
"""Immigration writer — 2026-05-26 17:00 PDT run"""
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

# ─────────────────────────────────────────────
# ARTICLE 1: F-1 Visa Revocation Wave
# ─────────────────────────────────────────────

article1_body = """Indian families have spent lakhs sending their children to American universities. Now some of those students are receiving emails telling them their legal status has been terminated — no hearing, no warning, no appeal window that matters.

Colleges across the United States are reporting a wave of unexpected F-1 visa revocations. The State Department and Department of Homeland Security have been quietly terminating students' SEVIS records — the digital lifeline that ties a foreign student's enrollment to their legal right to remain in the country. When the SEVIS record dies, the student's authorized stay dies with it.

## The mechanics of a revocation

A SEVIS termination is not a gentle nudge. Once a student's record is terminated, they are immediately out of status. They cannot attend classes. They cannot work. They are expected to leave the country, and every day they remain counts against them for future visa applications. Universities are finding out at the same time as the students, sometimes after.

The government does not need to provide a reason. Under existing regulations, the State Department can revoke a visa at any time, and courts have historically given the executive branch wide latitude on these decisions. A recent judicial ruling upheld SEVIS terminations for a group of Indian students, finding that the government acted within its authority — a precedent that has sent a chill through international student communities from Purdue to UT Dallas.

## Why Indian students are disproportionately exposed

Indians are the second-largest group of international students in the United States, behind only China. In the 2024-25 academic year, over 330,000 Indian nationals held F-1 status. They are concentrated in exactly the fields — computer science, engineering, data science, business analytics — that the administration has flagged for enhanced vetting.

The expanded social media screening announced by Secretary Rubio adds another dimension of risk. Students whose WhatsApp groups, Instagram stories, or X posts touch on political topics, protest movements, or even casual criticism of U.S. policy now face the possibility that a consular officer — or an algorithm — will flag their account for review. The screening applies retroactively to existing visa holders, not just new applicants.

For Indian families, the financial exposure is staggering. A year of tuition, housing, and living expenses at a mid-tier U.S. university runs $45,000 to $65,000. At an IIT or NIT, the same education costs under ₹3 lakh. An Indian family that has taken an education loan of ₹40-50 lakh against their home now faces the prospect of their child being sent back mid-semester with no degree and a loan that still needs repaying.

## The lawsuit

A group of Indian and Chinese students has filed suit against the Trump administration, challenging the revocations as arbitrary and procedurally deficient. Their core argument: the government terminated their status without providing specific reasons or an adequate opportunity to respond, violating due process protections that even non-citizens are entitled to under the Fifth Amendment.

The case faces steep odds. Courts have traditionally deferred to the executive on immigration enforcement, and the Supreme Court's recent rulings have only widened that deference. But the students' lawyers argue that mass revocations without individualized review cross a line that even plenary power doctrine does not protect.

## What Indian students should do now

Immigration attorneys are advising current F-1 holders to take several precautionary steps. First, audit your social media — not to self-censor, but to understand what a reviewer would see. Second, ensure your SEVIS record is current and your enrollment status is clean; any lapse in full-time enrollment, unauthorized work, or late paperwork gives the government an easy hook. Third, maintain copies of every university communication, enrollment verification, and I-20 document.

Students on OPT or STEM OPT face additional vulnerability. Their work authorization is derivative of their F-1 status — if the visa goes, the work permit goes with it, and their employer receives a notice that they are no longer authorized.

The broader message is blunt: the margin for error has collapsed. An F-1 visa in 2026 is not the stable platform it was five years ago. Indian families weighing whether to send a child to the U.S. — or keep one there — are now factoring in a risk that used to be theoretical: the possibility that the government will simply decide, one Tuesday morning, that their student's presence is no longer welcome."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "They Got an Email Saying It Was Over — Inside the F-1 Visa Revocation Wave Hitting Indian Students",
    "subheadline": "Colleges are reporting unexpected SEVIS terminations. Indian and Chinese students are suing. And a court just ruled the government was within its rights.",
    "slug": make_slug("f1-visa-revocation-sevis-indian-students-wave"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Over 330,000 Indian nationals hold F-1 status in the US. They are concentrated in STEM fields now under enhanced vetting. Indian families who have taken ₹40-50 lakh education loans face the prospect of a mid-semester deportation with no degree and a debt that follows them home.",
    "tags": ["f1-visa", "sevis", "student-visa", "immigration", "indian-students"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Associated Press (via Enterprise Journal)", "url": "https://www.enterprise-journal.com/colleges-around-us-say-some-international-students-visas-are-being-revoked"},
        {"name": "Newswall", "url": "https://www.newswall.org/story/international-students-are-being-told-by-email-that-their-visas-are-revoked-and-that-they-must-lsquo-self-deport-rsquo-what-to-know"},
        {"name": "ZTNDZ (SEVIS ruling)", "url": "https://ztndz.com/story23323267/judges-upheld-sevis-terminations-for-indian-students"},
        {"name": "Today FM", "url": "https://todayfmlive.com/trump-administration-orders-embassies-to-halt-student-visa-appointments/"}
    ]),
    "score_total": 85,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg",
    "body": article1_body
}

# ─────────────────────────────────────────────
# ARTICLE 2: Kolkata B1/B2 Pilot
# ─────────────────────────────────────────────

article2_body = """If you have been trying to bring your parents to the United States for a graduation, a grandchild's birthday, or just a few months together, you already know the drill. Book a B1/B2 appointment at the nearest U.S. consulate in India. Wait. Wait longer. Discover the next available slot is fourteen months away. Watch the occasion pass.

The U.S. Consulate in Kolkata has quietly changed the math — at least for some applicants. A new pilot programme, launched in May 2026, creates priority appointment tracks for two groups that matter enormously to the Indian American community: parents aged 50 and above visiting children in the U.S., and verified business travellers.

## What actually changed

The Kolkata consulate now offers faster B1/B2 interview slots to parents who meet specific criteria: they must be 50 or older, visiting a child who legally resides in the United States (citizen, green card holder, or valid long-term visa holder), and able to demonstrate genuine travel purpose alongside strong ties to India.

A separate priority track targets business travellers with verified commercial reasons — meetings, conferences, contract negotiations, corporate training. The consulate has framed this under the banner of supporting trade and investment between India and the United States.

There is also a third, unconfirmed change. Some applicants choosing Kolkata as their interview location have reported seeing new B1/B2 sub-categories during the application process: Business Professionals, Parents Visiting Children with Legal Status, General Tourism & Travel (for applicants with no prior refusals), and Recent Visa Refusal (within 24 months). The consulate has not officially acknowledged these categories, and applicants should treat them cautiously.

## The wait-time context

To understand why this matters, consider the numbers. India's four consulates and one embassy process over 1.2 million nonimmigrant visa applications per year. Wait times for first-time B1/B2 appointments have stretched past a year at some posts. The State Department's own data shows Kolkata's median wait had dropped to 30 days as of May 25 — a significant improvement from where it was a year ago, and now potentially even faster for eligible parents.

For Indian Americans, the parent visit is not a luxury trip. It is how families function across 8,000 miles. A mother flies to help after a delivery. A father comes for a daughter's graduation. Retired parents spend winters with their children rather than alone in Pune or Chennai. When appointment backlogs stretched past a year, these rhythms broke. Babies arrived without grandparents present. Graduations were celebrated over video call.

## What it does not do

Priority scheduling is not priority approval. A faster appointment brings the interview forward; it does not change what happens in the interview room. The consular officer still applies the same standard every B1/B2 applicant faces — proof that the visit is temporary and that the applicant intends to return to India. A quicker date does not lower that bar.

It is also, critically, limited to Kolkata. There is no confirmation that the pilot will expand to Delhi, Mumbai, Chennai, or Hyderabad. For most Indian applicants, the nearest consulate is not Kolkata, and switching interview locations has logistical consequences — travel to the interview city, document handling, appointment availability at the new post.

## The "America First in Family Values" framing

The consulate has branded the parents' track under the theme "America First in Family Values" — a notable rhetorical choice during an administration that has otherwise moved aggressively to restrict immigration at nearly every other touchpoint. The framing suggests an awareness that visitor visa backlogs for elderly Indian parents are politically indefensible even within a restrictionist framework. These are not economic migrants. They are grandparents.

Whether the branding reflects a genuine policy priority or a local consulate initiative designed to manage its own queue more efficiently is unclear. What is clear is that the pilot creates a small, useful pressure-release valve for a community that has been asking for one.

## What NRIs should do

If your parents are 50 or older and you can make Kolkata work as an interview location, this is worth exploring — but not blindly. Verify current eligibility criteria on the official U.S. Travel Docs India portal before making any changes. Ensure their DS-160 is accurate and matches supporting documents. Prepare strong evidence of ties to India: property, pension, family obligations. And do not assume a faster appointment means a softer interview.

For those whose parents interview at other consulates, the Kolkata pilot is still worth watching. Successful pilots tend to expand. And in a year where nearly every immigration development has been bad news, a programme that explicitly says "bring your parents faster" is, at minimum, a signal that someone in the system remembers what these visas are actually for."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Your Parents Just Got a Fast Track — Inside Kolkata's New Priority Visa Pilot for Indian Families",
    "subheadline": "The U.S. Consulate in Kolkata is testing priority B1/B2 appointments for parents over 50 visiting children in America. Here is exactly what changed and what did not.",
    "slug": make_slug("kolkata-consulate-b1b2-priority-pilot-indian-parents"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian Americans have watched their parents wait 12-14 months for a visitor visa appointment while graduations, births, and family milestones passed without them. Kolkata's pilot creates priority slots specifically for parents 50+ visiting children in the US — the exact use case that has caused the most pain in the NRI community.",
    "tags": ["b1b2-visa", "kolkata-consulate", "visitor-visa", "indian-parents", "immigration"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "IMAD Travel", "url": "https://imadtravel.com/blog/us-consulate-kolkata-b1-b2-visa-pilot-2026/"},
        {"name": "WaitVisa (State Department data)", "url": "https://waitvisa.com/consulates/kolkata"},
        {"name": "US Travel Docs India", "url": "https://www.ustraveldocs.com/in/"}
    ]),
    "score_total": 72,
    "status": "published",
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/37669246/pexels-photo-37669246.jpeg",
    "body": article2_body
}

# ─────────────────────────────────────────────
# Publish
# ─────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
