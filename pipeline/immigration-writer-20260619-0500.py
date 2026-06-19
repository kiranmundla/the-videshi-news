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

article1_body = """Of all the levers Washington can pull to make life harder for foreign students, few are as quiet — or as consequential — as the number of days they get to stay after the music stops. A proposed Department of Homeland Security rule would cut that cushion in half, from 60 days to 30, and immigration lawyers say Indian students will feel it first and worst.

The grace period is the window an F-1 student gets once their program or work authorization ends. It is the time to pack up, change status, line up a job, or leave the country without falling out of legal standing. Sixty days is tight. Thirty is barely a month to find an employer willing to sponsor an H-1B, file the paperwork, and pray the lottery gods smile.

## The Day 1 CPT squeeze

The proposed rule does more than shorten a clock. Buried in the same regulatory push is language that would narrow "Day 1 CPT" — the practice of enrolling in a new academic program that authorizes work from the first day of classes. For thousands of Indian graduates who strike out in the H-1B lottery, Day 1 CPT has been the bridge that keeps them legally employed while they roll the dice again the following year.

Cyrus Goldman, an immigration attorney who spoke about the proposal, put the problem plainly: someone who already holds a master's degree cannot simply go back and claim they need another master's to justify work authorization. The escape hatch closes.

"For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" Goldman said.

## Why this lands on Indian students hardest

Indians are the largest single nationality in the U.S. international-student population and account for an outsized share of H-1B lottery entries. The pipeline is familiar to nearly every NRI family: an F-1 visa, a STEM degree, a year or three of Optional Practical Training, and then the annual H-1B scramble. Each narrowing of the path compounds for a group that is already over-represented at every stage.

The fields most exposed are exactly the ones Indian students cluster in — artificial intelligence, machine learning, software engineering, data science. These are also the roles American employers say they cannot fill domestically, which is why Goldman warns the pain will not stay confined to students.

"There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said. Foreign nationals make up a substantial slice of the U.S. AI workforce, and a 30-day grace period gives neither the worker nor the employer room to maneuver.

## What employers may do next

Companies are not without options, but the alternatives are narrower and pricier. Cap-exempt H-1B sponsorship through universities and nonprofits remains available. The O-1 visa, reserved for individuals of "extraordinary ability," is a route for the genuinely exceptional but useless for the median new graduate. Both require planning that a one-month window does not allow.

"The companies will either struggle because they won't have the talent or they will have to get creative and find alternate solutions," Goldman said.

## What's next

The rule is a proposal, not yet law, which means a public comment period and the near-certainty of litigation before anything takes effect. That is cold comfort for a student graduating in May 2027 who cannot plan around a rule that may or may not exist by then. For now, the practical advice from immigration counsel is unglamorous: file early, keep status documents pristine, and do not assume the 60-day cushion will be there next year. The trend line, across grace periods, OPT, and the lottery itself, points in one direction — and it is not toward more time."""

article2_body = """The American dream, for a certain kind of immigrant, has a familiar arc: arrive on a student visa, win the H-1B lottery, climb to a green card, and finally raise a hand to swear the oath of citizenship. A case unsealed by the Department of Justice this week is a reminder that the last step is no longer always the final one.

The DoJ announced it had filed denaturalization actions in federal district courts against 17 individuals, among them Neeraj Sharma, an India-born former owner and chief executive of Magnavision LLC, a staffing company based in New Jersey. The government wants his 2017 citizenship revoked.

## What the government alleges

According to the filing, Sharma signed and submitted eleven fraudulent H-1B petitions to U.S. Citizenship and Immigration Services. Each petition, prosecutors say, falsely claimed the visa beneficiaries would work at a particular global financial institution, and each was padded with letters on corporate letterhead bearing forged signatures of company executives.

The naturalization itself is the second alleged offense. When Sharma applied to become a citizen in 2017, he attested under penalty of perjury that he had never committed an unprosecuted crime, never given false information to a government official, and never lied to obtain an immigration benefit. USCIS approved his application on the strength of those statements. The government now says all three were false.

Under the Immigration and Nationality Act, citizenship obtained by "concealment of a material fact" or "willful misrepresentation" can be stripped, and the certificate of naturalization canceled — turning a citizen back into a non-citizen, subject to removal.

## The body-shop shadow over a legitimate program

For the Indian diaspora, this case touches a nerve that has nothing to do with sympathy for fraud and everything to do with reputation. The so-called "body shop" model — small staffing firms that file large volumes of H-1B petitions, sometimes for jobs that do not exist or clients who never asked — has long dogged the program. Indians run many of these firms and fill most of these visas; more than 70 percent of approved H-1B petitions go to workers born in India.

When a Magnavision surfaces, it hands ammunition to those who argue the entire program is riddled with abuse. Every honest engineer at a Fortune 500 company pays a small reputational tax for the actions of a fraudster they have never met.

## Why naturalized Indian Americans should pay attention

Denaturalization was once vanishingly rare, reserved for war criminals and the most egregious fraud. The filing of 17 cases at once signals a more aggressive posture. For the roughly hundreds of thousands of naturalized Indian Americans, the unsettling takeaway is not that honest citizens are at risk — they are not — but that the finish line is being re-examined years after it was crossed.

The practical lesson is narrower and worth stating clearly: the accuracy of every form filed on the journey, from the first H-1B petition to the final N-400, can be revisited. Misstatements that seemed minor at the time — an inflated job title, a client letter someone else prepared — live on in a file that the government can reopen.

## What's next

Denaturalization is a civil process, and Sharma will have the chance to contest the allegations in court. But the message the DoJ intends to send is already delivered. For a community that has treated citizenship as the safe harbor at the end of a long and uncertain voyage, the harbor now feels a degree less secure — not because the rules changed, but because the enforcement did."""

article3_body = """While the lawyers argue over fees and the consulates ration appointment slots, India's diplomats in America are doing something quieter and, for anxious families back home, more reassuring: picking up the phone.

Officials from the Indian Embassy in Washington and its consulates held a virtual interaction this week with Indian students from across the United States, a session led by Charge d'Affaires Ambassador Sripriya Ranganathan. Around 150 Indian Student Association office bearers from 90 American universities joined, alongside the Consuls General of India in Atlanta, Chicago, Houston, New York, San Francisco, and Seattle.

## A meeting with a backdrop

The timing is not incidental. The session lands during the worst stretch for Indian student mobility in years. Education consultants in Hyderabad report a 70 to 80 percent drop in students heading to U.S. universities this cycle, a collapse driven by frozen visa-appointment slots, a spike in rejections, and a vetting regime that now scrapes applicants' social media. Students who managed to book interview slots say they have received no confirmation. Many have simply given up and looked to Britain, Canada, or Australia.

Against that, a webinar can seem like a small gesture. But for parents in India watching their children navigate a hostile system 8,000 miles away, knowing the embassy is reachable carries real weight.

## What was discussed

The conversation centered on student well-being and on practical ways to stay connected to the diplomatic missions. Ranganathan urged students to register on the embassy and consulate websites, to familiarize themselves with safety guidelines, and to keep emergency contact details for the missions close at hand.

"Cd'A @ranganathan_sr, along with Consul Generals of India in the US, held a virtual interaction with Indian students from universities across the US, discussed aspects of student wellbeing, and suggested ways to stay connected with the Embassy, Consulates and the larger Indian diaspora," the Indian Embassy wrote on X.

The students, for their part, offered suggestions on coordinating among the embassy, universities, and diaspora organizations — a sign the missions are trying to build a standing network rather than respond case by case.

## The safety dimension

There is a somber thread running beneath the well-being talk. A spate of deaths of Indian and Indian-origin students at American universities over the past year has rattled the community, and the embassy's outreach drive carries that weight. Registration on consular websites is not bureaucratic box-ticking; it is how a mission locates a student in a crisis, reaches a family, or coordinates with local authorities.

## Why this matters to the diaspora

For NRIs, the consulate is often an abstraction — a place you visit once for an OCI card and then forget. This outreach is a reminder that the missions are also a safety net, and that the net only works if students are in it. The push to register, to know the emergency numbers, to stay connected, is aimed squarely at the families who will read this and text their kids to sign up.

It is also a quiet acknowledgment from New Delhi that its students are under unusual stress in America right now, and that the government is watching. That will not unfreeze a single visa slot. But in a season defined by uncertainty, a diplomat saying "we are here, and here is how to reach us" is not nothing.

## What's next

The embassy signaled this will be an ongoing effort rather than a one-off. Students were asked to spread the word among peers, and the missions indicated they want to synergize with university authorities and diaspora groups. For families weighing whether America is still worth the trouble, the message from India's diplomats is that whatever Washington decides, their own government intends to stay within reach."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The 60-Day Cushion That Saved Indian Grads Is About to Be Cut in Half",
        "subheadline": "A proposed DHS rule would shrink the F-1 grace period to 30 days and choke off Day 1 CPT — the lottery loser's lifeline that Indian students lean on most.",
        "slug": make_slug("f1-grace-period-30-days-day1-cpt-indian-students-dhs-rule"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the largest international-student group and dominate the H-1B lottery, so halving the F-1 grace period and narrowing Day 1 CPT removes the fallback that keeps Indian graduates legally employed after a lottery loss.",
        "tags": ["f1-visa", "opt", "cpt", "students", "uscis", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — Tighter student visa rules may impact Indians", "url": "https://theindianeye.com/"},
            {"name": "Khabar — Immigration News Briefs", "url": "https://www.khabar.com/"},
            {"name": "Inside Higher Ed — Students Still in Limbo", "url": "https://www.insidehighered.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students walk across a university campus on a bright day",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The DoJ Wants to Take Back a Citizenship It Granted in 2017 — Over Forged H-1B Petitions",
        "subheadline": "An India-born New Jersey staffing executive is among 17 facing denaturalization, a once-rare action now being used more aggressively against naturalized Americans.",
        "slug": make_slug("denaturalization-h1b-fraud-magnavision-neeraj-sharma-doj-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With more than 70% of H-1B petitions going to Indians and many staffing 'body shops' run by Indian Americans, a wave of denaturalization cases tied to visa fraud reopens scrutiny of citizenships the diaspora long treated as settled.",
        "tags": ["h1b", "denaturalization", "doj", "fraud", "citizenship", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — H-1B visa fraud leads to revocation of US citizenship", "url": "https://theindianeye.com/"},
            {"name": "U.S. Department of Justice", "url": "https://www.justice.gov/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/6b/Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg/1280px-Jamaica_Av_153rd_St_td_%282022-04-11%29_02_-_USCIS_Application_Support_Center.jpg",
        "image_caption": "A USCIS Application Support Center in Jamaica, Queens, New York",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "India's Diplomats Are Calling Their Students in America — and the Timing Says Everything",
        "subheadline": "As US visa slots stay frozen and arrivals crater, the Indian Embassy convened students from 90 universities for a reason that goes beyond well-being.",
        "slug": make_slug("indian-embassy-virtual-student-outreach-visa-freeze-safety"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "With Indian student arrivals down 70-80% and a string of student deaths rattling families, India's consular outreach is a reminder to NRIs that the missions are a safety net that only works if students register and stay connected.",
        "tags": ["students", "indian-embassy", "consulate", "f1-visa", "diaspora-safety", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — Indian Embassy and Consulates virtual interaction with students", "url": "https://theindianeye.com/"},
            {"name": "The Indian Eye — Visa crisis prompts 70-80% drop in Indian students", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66/Indian_Embassy_Women%27s_Day_celebration_at_the_Embassy_of_India_in_Washington%2C_D.C._on_7_March_2024_-_11.jpg/1280px-Indian_Embassy_Women%27s_Day_celebration_at_the_Embassy_of_India_in_Washington%2C_D.C._on_7_March_2024_-_11.jpg",
        "image_caption": "An event at the Embassy of India in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    if wc < 400:
        print(f"⚠️ {art['slug']}: only {wc} words — skipping")
        continue
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
