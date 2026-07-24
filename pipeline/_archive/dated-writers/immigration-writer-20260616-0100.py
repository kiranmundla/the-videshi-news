#!/usr/bin/env python3
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
        "headline": "The Student Visa Portal Opened, the Servers Buckled, and India Rushed the Gate",
        "subheadline": "Appointment slots for the fall intake went live this week and immediately jammed. The embassy says thousands booked for July and August, but the scramble exposes how thin the margin has become.",
        "slug": make_slug("us-student-visa-appointment-portal-crash-india-july-august-fall-intake"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For the tens of thousands of Indian families with a son or daughter holding a fall 2026 admit, the difference between a July interview slot and no slot is the difference between flying out on time and forfeiting a deposit.",
        "tags": ["f1-visa", "student-visa", "us-embassy-india", "opt", "fall-2026"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "India Tribune / ANI", "url": "https://www.indiatribune.com/us-embassy-in-india-assures-more-student-visa-appointments-in-coming-weeks/"},
            {"name": "Reuters (LL.M. applications)", "url": "https://www.reuters.com/legal/legalindustry/us-law-schools-see-sharp-drop-international-student-applications-2026-06-13/"},
            {"name": "Collegedunia (Parliament data)", "url": "https://collegedunia.com/news/indian-students-in-us-drop-2026"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/65/Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_12.jpg/1280px-Visitors_to_the_U.S._Embassy_New_Delhi_in_July_2023_12.jpg",
        "image_caption": "Visa applicants queue outside the U.S. Embassy in New Delhi during the summer interview season.",
        "image_attribution": "Wikimedia Commons",
        "body": """When the U.S. Embassy in New Delhi opened student visa appointment slots on June 14, the portal did what an underbuilt system does when a year of pent-up demand hits it at once: it stalled. Applicants reported pages timing out, accounts locking, and slots vanishing between the click and the confirmation. By the next morning the embassy was issuing the digital equivalent of a crowd-control announcement — *please don't refresh too often* — and promising that more appointments were on the way.

This is the part of the immigration story that rarely makes the policy briefings but matters most to families: the plumbing. An admit letter from a U.S. university is worthless without an F-1 visa, and an F-1 visa requires an interview, and the interview requires a slot on a portal that, this week, could not keep up.

## What the embassy actually said

By June 15, the embassy struck a reassuring tone. "Since June 14, thousands of students have secured visa appointments for July and August," it posted. "Thousands of appointments remain available and we will open thousands more in the coming weeks. We appreciate your patience as we diligently work to resolve the technical issues you have encountered."

Read carefully, that is both a promise and an admission. The promise: capacity is coming. The admission: the system that gates entry to American higher education for the world's largest cohort of foreign students wobbled on the first day of the rush.

## Why the rush is sharper this year

The crush is not happening in a vacuum. Indian student enrollment in the United States has been sliding — down 6.9% in a single year to roughly 352,000, according to data India's Ministry of External Affairs gave the Rajya Sabha, the sharpest annual drop in over a decade. At the graduate level the picture is starker. U.S. law schools have reported a more than 20% fall in international LL.M. applications, with India down 23%. Business schools, heavily dependent on international master's students, have been hit hardest of all.

Layer on last year's pause in visa interviews, expanded social media vetting, and roughly 8,000 student visa revocations, and you get a system where supply was already constrained when this year's applicants arrived. The students who held on through the uncertainty are now competing for a finite number of summer interview slots, all at once, on a portal that buckled.

## The deposit clock is the real pressure

For Indian families, the timing is unforgiving. Most U.S. universities required a non-refundable enrollment deposit by May 1. Having paid it, a student now needs a visa in hand before orientation in August. A July or early-August interview slot keeps the plan alive. No slot, and the choice narrows to a deferral request — not guaranteed — or a forfeited deposit and a lost year.

That is why the portal jam landed as something closer to panic than inconvenience. A few hundred dollars of deposit and a year of one's life are riding on server capacity in the second week of June.

## What to watch

Two things will tell Indian applicants whether this week was a hiccup or a warning. First, whether the embassy delivers the additional slots it promised, fast enough to clear the July–August window before classes start. Second, whether the technical fixes hold when the next wave of applicants logs on — because the demand behind this week's crash has not gone anywhere.

The State Department has signaled it wants to keep India's pipeline open; officials have repeatedly called the country a priority for visa processing. But intent and infrastructure are different things. For a family in Hyderabad or Pune watching a loading spinner at 3 a.m., the priority that counts is the one that produces an appointment confirmation.

For now, the advice from those who navigated the week successfully is unglamorous: keep checking, but not obsessively, since rapid refreshing can lock an account; have documents ready so a slot can be claimed the instant one appears; and treat a deferral conversation with the admissions office as a live backup, not a last resort. The students who get to campus this fall will be the ones who treated the portal as the obstacle it has quietly become."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Classrooms Are Quietly Emptying of Indians — and the Bill Is Coming Due",
        "subheadline": "International LL.M. applications from India fell 23% this year, graduate enrollment is down across the board, and universities that ran on foreign tuition are cutting staff. The diaspora pipeline is thinning at the source.",
        "slug": make_slug("indian-graduate-enrollment-collapse-us-universities-llm-budget-cuts"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The Indian-American professional class has historically been built on the student-to-H-1B-to-green-card pipeline; if the first link is breaking, the entire community's growth engine slows a decade from now.",
        "tags": ["international-students", "graduate-enrollment", "f1-visa", "opt", "universities"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/legal/legalindustry/us-law-schools-see-sharp-drop-international-student-applications-2026-06-13/"},
            {"name": "Inside Higher Ed", "url": "https://www.insidehighered.com/news/global/international-students"},
            {"name": "Marketplace", "url": "https://www.marketplace.org/story/falling-international-student-enrollment-economic-woes"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/19579986/pexels-photo-19579986.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Graduates in caps and gowns at a university commencement ceremony.",
        "image_attribution": "Pexels",
        "body": """The numbers arrive in fragments — a law school here, a business school there — but assembled, they describe something structural. American higher education, which for two generations has run partly on the tuition and the talent of Indian students, is seeing that flow shrink. And unlike a policy that can be reversed with a signature, a thinned applicant pool takes years to refill.

Start with the most concrete data point. International applications to U.S. law schools' LL.M. programs — the one-year master's degree that foreign-trained lawyers use to study American law — fell more than 20% this cycle. India, traditionally one of the two largest source countries, was down 23%. China fell 21%. "There is a feeling that the United States, generally speaking, is maybe not as welcoming to international students as it used to be," the Law School Admission Council's Gisele Joachim told Reuters.

## A broad-based retreat, not a blip

Law is not an outlier. An *Inside Higher Ed* analysis of nine universities found graduate international enrollment down an average of 29% year over year. NAFSA, the association for international educators, had projected a 15% sector-wide decline with steeper drops for master's programs — and the campus data has largely confirmed the gloomy forecast. Master's programs in computer science and STEM, the exact fields that funnel Indian graduates into the tech workforce, have been "mostly affected," NAFSA's CEO said.

The India-specific figures sharpen the point. New Indian arrivals dropped 44% at the campuses surveyed by one tracker. Parliament data in New Delhi pegged the total Indian student population in the U.S. at about 352,000, down 6.9% and the steepest annual fall in over a decade. For the first time since 2019, the gap between India and second-ranked China has narrowed — not because China surged, but because India slid.

## The money was never abstract

International students are not a rounding error on a university budget; they are, for many institutions, the budget. They typically pay full freight, subsidizing domestic students and entire departments. When they stop coming, the consequences are immediate and physical. DePaul University imposed faculty pay cuts and a hiring freeze. Niagara University cut staff. Ohio State reported a 38% drop in new international students; Indiana University, 30%; the University of Central Missouri, 50%.

NAFSA's projection is blunt about the spillover: this fall alone, the drop in enrollment has cost the U.S. economy an estimated $1.1 billion and nearly 23,000 jobs. "For every three international students, one U.S. job is created and supported," the group's chief executive said — in education, health insurance, transportation, retail, and the towns that revolve around campuses.

## Why this is a diaspora story, not just a campus story

Here is the part that should concern Indian-Americans specifically. The community's professional ascent in the United States has run along a well-worn track: arrive as an F-1 student, convert to OPT and then STEM OPT, win the H-1B lottery, and eventually file for a green card. Every link in that chain begins with a student visa. When the number of Indians entering U.S. graduate programs falls by a third, the effect does not show up this year — it shows up a decade from now, in a smaller cohort of Indian-origin engineers, founders, and physicians moving through the system.

The causes are familiar to anyone who has followed the past year: last spring's pause in visa interviews, expanded social media vetting, roughly 8,000 visa revocations, and a steady drumbeat of uncertainty around whether OPT — the post-study work bridge that makes a U.S. degree financially rational — will survive. When the work-after-graduation route looks shaky, the calculus of a $100,000 master's degree changes, and students who once chose Boston or Pittsburgh increasingly look at Toronto, London, or Melbourne instead.

## The competition is real

Universities know it. With Chinese enrollment also declining, 57% of U.S. graduate programs now say they are prioritizing India in recruitment, and roughly half of all institutions are targeting India for undergraduate outreach. Schools are offering more conditional admissions and deferrals to hold cohorts together while the visa system catches up.

But recruitment brochures cannot fix a perception problem rooted in policy. The students deciding right now whether to gamble on a U.S. degree are weighing tuition against the odds of a visa, a job, and a future. For a growing share of talented Indians, the math no longer obviously points to America — and the classrooms, and eventually the workforce, will reflect that choice."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Modi Takes the H-1B Fight to the G7 — With a Trade Deal Dangling as Leverage",
        "subheadline": "On the sidelines of the summit, the Indian prime minister is expected to press Washington on visas while both sides race to close the first tranche of a bilateral trade agreement by mid-July.",
        "slug": make_slug("modi-trump-g7-h1b-visas-india-us-trade-deal-bilateral"),
        "category": "immigration",
        "vertical": "geopolitics",
        "diaspora_angle": "If New Delhi can tie H-1B access to a trade deal Washington wants, the millions of Indians whose American futures hinge on work visas suddenly have a government negotiating on their behalf at the highest level.",
        "tags": ["h1b", "modi", "trump", "g7", "india-us-trade", "diplomacy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/world/india-modi-trump-likely-meet-g7-discuss-trade-visas-2026-06-10/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/us-to-launch-new-plan-for-work-visas-in-december-likely-to-benefit-the-indians-most/"}
        ]),
        "score_total": 79,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/09/President_Donald_Trump_and_Prime_Minister_Narendra_Modi_at_the_White_House.jpg/1280px-President_Donald_Trump_and_Prime_Minister_Narendra_Modi_at_the_White_House.jpg",
        "image_caption": "U.S. President Donald Trump and Indian Prime Minister Narendra Modi at the White House.",
        "image_attribution": "Wikimedia Commons",
        "body": """Diplomacy and immigration rarely sit at the same table. This week, on the sidelines of the G7 summit, they are expected to. Indian Prime Minister Narendra Modi is set to hold bilateral talks with U.S. President Donald Trump, and according to an Indian government source with direct knowledge of the planning, the agenda is unusually concrete: trade, energy, and — for the first time at this level in a while — H-1B visas.

"The prime minister is expected to hold talks on the trade ties, energy cooperation, and also take up the issue of H-1B visas," the source told Reuters. That single sentence is more significant than it looks, because it signals that New Delhi intends to treat the visa question not as a grievance to be aired but as a chip to be played.

## The leverage is the trade deal

The reason this meeting carries weight is timing. India and the United States are moving toward the first tranche of a bilateral trade agreement, which India's Trade Minister Piyush Goyal has said could be concluded by mid-July. Washington wants the deal; it has proposed an additional 12.5% tariff on Indian goods over forced-labor allegations India rejects, and broader tariff friction has strained ties for months. New Delhi, for its part, is pushing for preferential tariff treatment.

That gives Modi something he has not always had in visa conversations: a counterweight. When the only item on the table is "please be kinder to our nationals," India is asking for a favor. When the table also holds a trade agreement the U.S. administration wants to announce, the H-1B becomes a bargaining item rather than a plea. Whether India actually links the two explicitly is the question diaspora professionals should watch.

## Why H-1B is suddenly negotiable

The backdrop is a year of upheaval for the program. The Trump administration imposed a $100,000 fee on new H-1B petitions filed from outside the country — a policy a federal judge struck down as an unauthorized tax before it was temporarily stayed on appeal. The lottery has been rewritten to favor higher-wage, higher-skilled applicants. Consular vetting has expanded. Indians, who account for more than 70% of approved H-1B petitions annually, have borne the brunt of every one of these changes.

Against that, there is one genuinely positive development that India has every reason to consolidate at the G7: the domestic visa renewal pilot. Beginning in December, the State Department plans to issue 20,000 visas to foreign nationals already inside the United States, allowing them to renew without flying home. Julie Stufft, Deputy Assistant Secretary of State for Visa Services, was explicit that the program is "focused very much on India" and that "the vast majority of those will be Indian nationals living in the US." A formal Federal Register notice laying out eligibility is expected soon.

## What a win would look like

For the millions of Indians whose American lives run through the H-1B, a successful Modi-Trump exchange would not produce a single dramatic announcement. It would produce smaller, durable things: a firm start date and expanded scope for the domestic renewal pilot; assurances on consular appointment capacity; perhaps a quiet understanding that the most punitive fee proposals stay shelved while the trade deal is alive.

None of that is guaranteed. The meeting comes at what Reuters called "a delicate moment," with tariffs unresolved and Trump's repeated claims about mediating last year's India-Pakistan conflict — which India flatly denies — still irritating the relationship. Secretary of State Marco Rubio's visit to New Delhi last month eased some tension, but the two governments are negotiating, not embracing.

## The diaspora stake

Still, this is one of the few moments when the interests of an Indian professional in Austin or Edison and the interests of the Indian state visibly align. The community cannot lobby Washington directly with much force. A prime minister sitting across from a president, with a trade deal both sides want to sign, can.

The outcome of the talks will not be measured in communiqués. It will be measured months from now, in whether the December renewal pilot launches on schedule and at scale, whether the $100,000 fee stays buried, and whether the visa appointment backlog in India eases. If Modi converts the trade leverage into even modest, concrete H-1B commitments, it will be the rare case of high diplomacy translating directly into the daily reality of a green-card-line family. If he does not, the diaspora is back to refreshing portals and reading visa bulletins on its own."""
    }
]

inserted = []
for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"OK  {art['slug']}  ({wc} words)")
        inserted.append(art["slug"])
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")

print(f"\n{len(inserted)}/{len(articles)} inserted")
