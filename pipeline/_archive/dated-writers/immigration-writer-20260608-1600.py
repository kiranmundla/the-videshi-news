#!/usr/bin/env python3
"""Immigration writer — 2026-06-08 16:00 UTC run.
Two articles:
1. OPT fraud crackdown + legislative threats (ICE 10K cases, Chip Roy bill, Landmark petition)
2. Day-1 CPT pathway closing under DHS Duration of Status rule change
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

# ─────────────────────────────────────────────
# Article 1: OPT Fraud Crackdown
# ─────────────────────────────────────────────

art1_body = """For nearly four decades, the Optional Practical Training programme gave international graduates something rare in American immigration: a clean, quiet transition from classroom to cubicle. A year of post-degree work experience — three years for STEM graduates — with no lottery, no employer petition, no six-figure filing fee. The programme worked so well that most Americans had never heard of it.

That anonymity is over. In the space of five weeks, OPT has been named a fraud magnet by federal law enforcement, targeted for outright elimination by a House bill, and challenged as unconstitutional by a conservative legal foundation. For the roughly 200,000 Indian students enrolled at American universities — the single largest nationality in the OPT pipeline — these converging threats amount to an existential crisis for the post-graduation pathway that underpins their entire immigration plan.

## Ten Thousand Red Flags

On May 14, Immigration and Customs Enforcement disclosed that investigators had identified more than 10,000 foreign students on F-1 visas working for what the agency called "highly suspect employers." Acting ICE Director Todd Lyons described OPT as a "magnet for fraud" and said field visits had turned up empty buildings, locked doors, and shell companies coordinating placements from India.

The pattern was consistent: companies filed legitimate-looking paperwork, collected fees from students desperate to maintain visa status, and provided fabricated employment records. No real work was performed. Students paid thousands of dollars for positions that existed only on paper, believing they were accumulating the practical experience their visas required.

Lyons said the 10,000 cases represented "only the tip of the iceberg." The investigation is expanding, and federal prosecutors are building criminal cases against the operators.

The fraud discovery arrived alongside a separate but related bust. U.S. authorities seized more than 100,000 fake degree certificates linked to Indian institutions, including Manav Bharti University, which allegedly sold credentials for as little as $1,400 each. USCIS admitted it does not track whether H-1B recipients obtained their qualifying degrees from institutions later found to be fraudulent — a gap that has allowed the problem to compound for years.

## The Kill Bill

Three weeks after ICE's announcement, Representative Chip Roy of Texas introduced the American White-Collar Worker Jobs Act on June 4. The legislation would eliminate OPT entirely, ending the programme that allows F-1 graduates to work in the United States after completing their studies.

Roy's bill goes further than any prior legislative attempt to curtail post-graduation employment. It would also end the H-1B's role as a pathway to permanent residency, replace the visa lottery with a wage-based selection system, shorten the maximum H-1B duration from six years to two, and require employers to certify that qualified American workers are unavailable.

The Federation for American Immigration Reform, US Tech Workers, and the Immigration Accountability Project have endorsed the bill. Kevin Lynn, president of US Tech Workers, said it would "address many of the egregious aspects of the H-1B visa programme."

Separately, the Landmark Legal Foundation has petitioned the Department of Homeland Security to rescind post-completion OPT through administrative action — no congressional vote needed. The foundation argues the programme violates the "major questions doctrine" because Congress never explicitly authorised DHS to create what amounts to a new worker visa category. OPT participants, Landmark notes, are no longer students. They are employees operating outside congressionally mandated visa caps.

## The Defence

Not everyone in Washington wants OPT dead. In March, Representatives Sam Liccardo, Jay Obernolte, and Raja Krishnamoorthi introduced the bipartisan Keep Innovators in America Act, which would codify OPT into statute for the first time — taking the programme out of DHS's administrative discretion and giving it the congressional blessing its critics say it lacks.

Representative Obernolte argued the United States cannot afford to "educate the world's most talented students in American institutions only to send them abroad to compete with us." The American Immigration Lawyers Association noted that international students contribute more than $40 billion annually to the U.S. economy.

The bill has bipartisan sponsorship but faces steep odds in a Congress where immigration restriction commands broader support than immigration expansion.

## What This Means for Indian Students

The stakes are not abstract. Indian nationals account for the largest share of OPT and STEM OPT participants. For most, the programme is not a luxury — it is the bridge between graduation and the H-1B lottery, the only window in which a freshly minted engineer or data scientist can work legally while waiting for the once-a-year visa draw.

If OPT vanishes, that bridge collapses. Students who spent $100,000 or more on American master's degrees in computer science, artificial intelligence, or electrical engineering would face a binary choice on graduation day: leave the country or find another visa category — a search that, for most, leads nowhere.

The fraud crackdown compounds the problem. Even students working for legitimate employers now face heightened scrutiny. Site visits are increasing. Documentation requirements are tightening. And the political narrative — OPT as a fraud pipeline rather than a talent pipeline — makes the programme harder to defend in the halls where its fate will be decided.

For the 200,000 Indian students currently in American classrooms, the next twelve months will determine whether the path they planned still exists when they cross the stage."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Ten Thousand Ghost Jobs — ICE Exposes a Shadow OPT Industry and Congress Wants the Programme Dead",
    "subheadline": "Federal investigators found shell companies in India placing students at empty offices. Now a House bill and a legal petition want to kill the entire post-graduation work programme.",
    "slug": make_slug("opt-fraud-10000-ghost-jobs-ice-chip-roy-kill-bill-indian-students"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian students are the largest nationality in the OPT pipeline. The programme is their only legal bridge between graduation and the H-1B lottery. If OPT disappears, roughly 200,000 Indian students lose their post-graduation work pathway.",
    "tags": ["opt", "stem-opt", "f1-visa", "ice", "fraud", "chip-roy", "indian-students", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Meyka", "url": "https://meyka.com/blog/ice-cracks-down-on-opt-fraud-may-14-10000-students-targeted-1405/"},
        {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/opinion/3437891/opt-out-reduce-fraud-preserve-american-jobs-eliminating-one-key-program/"},
        {"name": "Nagaland Post / IANS", "url": "https://nagalandpost.com/us-lawmaker-introduces-bill-seeking-major-h-1b-overhaul/"},
        {"name": "ABIL Immigration Insider", "url": "https://www.abil.com/resources/newsletter/"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/2294135/pexels-photo-2294135.jpeg",
    "image_caption": "An empty office hallway with closed doors — the kind of address ICE found when visiting OPT employers",
    "image_attribution": "Pexels",
    "body": art1_body
}

# ─────────────────────────────────────────────
# Article 2: Day-1 CPT Closing
# ─────────────────────────────────────────────

art2_body = """The workaround had a name everyone in the Indian tech community knew but nobody discussed in polite company. Day-1 CPT — Curricular Practical Training that started on the first day of a new master's programme — was the safety valve for thousands of engineers who lost the H-1B lottery and had no other way to keep working legally. Enrol in a second degree at one of the universities that offered immediate work authorisation, continue your job, and wait for the next lottery cycle.

It was legal. It was expensive. And it was the only reason many of America's best-trained Indian software engineers, machine-learning researchers, and data scientists did not board a flight to Hyderabad or Bangalore the day their OPT expired.

Now that safety valve is closing, and the people who designed their careers around it have no Plan B.

## The Rule That Changes Everything

On May 5, the Department of Homeland Security proposed eliminating the "Duration of Status" framework for F-1 student visas. Under the current system, international students can remain in the United States as long as they maintain valid student status — an open-ended arrangement that made Day-1 CPT possible.

The proposed rule replaces that flexibility with a hard ceiling: a fixed admission period of up to four years. Any extension beyond that — including cases involving continued studies or post-graduation work authorisation — would require formal approval from USCIS, an agency currently processing applications at timelines measured in months, not weeks.

"The duration of status rule that has been proposed is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training," said Danielle Goldman, co-founder and CEO of Build, an immigration advisory firm.

A second proposed change would cut the grace period after F-1 status ends from 60 days to 30 days — halving the window in which a student can find an employer willing to sponsor an alternative visa or file for a change of status.

## Why Day-1 CPT Mattered

To understand the panic, you need to understand the arithmetic of the H-1B lottery.

Each year, roughly 400,000 to 500,000 registrations compete for 85,000 H-1B slots. For Indian nationals — who constitute the largest share of applicants — the odds have been punishing for years. Lose the lottery once, and your employer can re-register the following year. Lose it twice, and your STEM OPT is running out. Lose it three times, and you are out of legal options — unless you enrol in a new degree programme that offers Day-1 CPT.

The universities that offered these programmes were not Ivy League institutions. Many were smaller, accredited schools that had built a business model around serving exactly this population: experienced professionals who needed a student visa to keep working while the lottery gods decided their fate. The tuition was steep — often $15,000 to $25,000 per year for a programme the student had no real intention of completing. Everyone understood the arrangement.

Goldman was blunt about what happens when this pathway disappears. "For anyone who already has a master's degree, they are not going to be able to go back and say, 'I need another master's degree because I need work authorisation to continue working,'" she told The Indian Eye.

## The Cascade

The Day-1 CPT closure does not operate in isolation. It arrives at the same moment that every other immigration pathway for Indian tech professionals is under pressure.

OPT itself faces an existential threat. ICE identified more than 10,000 fraudulent cases in May, and Representative Chip Roy's American White-Collar Worker Jobs Act proposes eliminating the programme outright. The H-1B lottery now uses a wage-weighted selection that penalises entry-level positions — exactly where new graduates land. The green card backlog for EB-2 India stretches past 862,000 applicants. And the $100,000 filing fee on new H-1B petitions has made smaller employers think twice about sponsoring anyone.

Each pathway narrowing individually would be manageable. Together, they form a closing vise. The student who loses the lottery can no longer fall back on Day-1 CPT. The graduate whose OPT expires cannot count on the programme surviving. The mid-career professional on an H-1B cannot afford to wait another decade for a green card that may never materialise.

Goldman warned that the impact extends beyond immigrants. "There's no doubt about it that this is going to have a massive impact on the companies that are in desperate need of top talent," she said, noting that foreign nationals make up a substantial portion of the American AI talent pool. Companies may pursue cap-exempt H-1B programmes or O-1 visas for extraordinary ability — options that work for the top five per cent of candidates and leave the other 95 per cent stranded.

## The Advice No One Wants to Hear

Goldman's counsel to Indian students was pragmatic to the point of bleak: develop multiple backup plans rather than relying on any single pathway. The H-1B lottery is not a strategy. Day-1 CPT is not a strategy. STEM OPT is not permanent. Every one of these programmes can be modified, restricted, or eliminated by a single rule change or a single congressional vote.

For thousands of Indian STEM workers who built their American lives on the assumption that the system, however slow, would eventually let them stay, that advice lands like a verdict. The rules they followed are being rewritten. The workarounds they depended on are being sealed. And the political environment in Washington offers no indication that relief is coming.

The door marked Day-1 CPT was never the front entrance. It was the side door that everyone pretended not to see. Now it is being bricked shut — and the queue at the front entrance has not moved in years."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "The Last Side Door Is Closing — Day-1 CPT Was Keeping Thousands of Indian STEM Workers in America",
    "subheadline": "A proposed rule ending open-ended student visas would kill the backup plan that Indian engineers have used for years after losing the H-1B lottery. The alternatives are thin.",
    "slug": make_slug("day-1-cpt-closing-dhs-duration-status-indian-stem-workers"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Day-1 CPT was the de facto safety net for Indian STEM professionals who lost the H-1B lottery. Without it, thousands of engineers in AI, ML, and data science face forced departure from the US.",
    "tags": ["day-1-cpt", "f1-visa", "duration-of-status", "h1b-lottery", "stem", "indian-students", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/06/02/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/us-bill-eyes-major-h-1b-overhaul-seeks-to-end-green-card-track"},
        {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com/news/world/us-lawmaker-proposes-major-h-1b-visa-overhaul-and-end-to-green-card-pathway/article69636843.ece"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4922086/pexels-photo-4922086.jpeg",
    "image_caption": "A person holding an opened passport — the document that defines the legal existence of hundreds of thousands of Indian workers in America",
    "image_attribution": "Pexels",
    "body": art2_body
}

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
