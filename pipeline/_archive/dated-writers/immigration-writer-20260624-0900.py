#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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

article1_body = """The Supreme Court spent Tuesday ruling on green cards, and the headline number — 6-3 — barely captures what changed for the people who hold them. In *Blanche v. Lau*, the justices decided that a border officer no longer needs "clear and convincing evidence" that a returning lawful permanent resident committed a crime before treating that resident as a stranger at the door rather than as someone who already belongs here. A charge is enough. The proof can come later, at a removal hearing, with evidence the government did not have when it took the green card.

For the roughly six million people of Indian origin in the United States — and the large share of them holding green cards rather than citizenship — this is the kind of ruling that does not make the morning news in Hyderabad but quietly rewrites the rules of the airport line.

## What the court actually held

The case involved Muk Choi Lau, a Chinese national who became a permanent resident in 2007, was charged with trademark counterfeiting, traveled to China while under indictment, and was paroled back into the country on his return rather than admitted as the resident he was. He was later convicted, and the government moved to deport him on the ground that he had been inadmissible the day he landed.

The Immigration and Nationality Act treats a returning green card holder as already admitted — spared the scrutiny new arrivals face — unless one of six exceptions applies. One exception covers a resident who "has committed" a crime involving moral turpitude. Justice Clarence Thomas, writing for the majority, declined to read a high evidence burden into that exception. Border officers, he wrote, must make "quick judgments on the spot," and Congress did not bury a clear-and-convincing standard in the statute.

Justice Ketanji Brown Jackson, joined by Justices Sotomayor and Kagan, called the result a "massive blank check." A green card, she warned, now means you belong here only until an officer decides otherwise — and the officer no longer needs proof to decide.

## Why this lands on Indian green card holders

The Indian diaspora is, by the numbers, a green card community waiting on citizenship. Decades-long EB-2 and EB-3 backlogs mean an Indian professional can hold permanent residency for ten or fifteen years before naturalizing. That long stretch as an LPR is exactly the window *Lau* makes riskier.

Consider how ordinary the trigger is. An old, sealed arrest. A DUI from a decade ago. A shoplifting charge that was dismissed. A pending case back in India that never reached trial. None of these is a conviction. After *Lau*, any one of them can route a returning resident — back from a parent's funeral in Pune or a cousin's wedding in Delhi — into secondary inspection, where the green card can be taken and the resident paroled in on a slip of paper, facing the harshest removal track the code offers.

The point is not that mass detentions of Indian travelers will begin tomorrow. It is that the legal floor under a green card has dropped. The document is now contingent in a way it was not on Monday.

## The practical takeaways

Immigration attorneys are already converging on the same advice. First, residents with any criminal history — however old, however minor, however far away — should consult a lawyer *before* booking international travel, not after landing. A disposition that seemed closed may now matter at the border.

Second, the ruling sharpens an argument the diaspora has heard for two years: for those eligible, naturalization is the only status the government cannot pause at an airport. A citizen returning from abroad cannot be paroled or stripped of status on a charge. With the N-400 fee set to climb roughly 75 percent under a separate DHS proposal, the math on "apply now versus wait" has shifted toward now for many.

Third, carry proof of status and keep records clean. The burden has quietly moved onto the traveler to demonstrate they are who their card says they are.

## What's next

The court sent Lau's own case back to the Second Circuit, which still must decide whether his crime qualifies as one of moral turpitude. But the rule the justices announced is final, and it applies the moment a green card holder presents themselves at a port of entry. For a community that has spent years treating the green card as the finish line before citizenship, *Blanche v. Lau* is a reminder that the line keeps moving — and that, for now, it is being drawn by whoever is working the booth."""

article2_body = """The fight everyone watched was the $100,000 H-1B fee, struck down this month by a Boston judge and now headed for appeal. The fight that will actually decide whether thousands of Indian professionals keep their visas is quieter, older, and already underway inside USCIS adjudication units: a surge in Requests for Evidence and denials aimed squarely at how a job's wage level is described on paper.

It is not a new rule. It is the slow, grinding application of an existing one — and for Indian workers, who fill the largest share of H-1B petitions, it is the difference between an approval and a scramble.

## The wage-level trap

Here is the mechanism. Every H-1B petition lists a Department of Labor wage level, from Level I (entry-level, closely supervised) to Level IV (senior, independent). USCIS adjudicators have been instructed to weigh wages when judging whether a role is a genuine "specialty occupation." The result, immigration firms report, is a wave of RFEs on petitions that pair a Level I wage with a job description that sounds too important for one.

The cruelty is in the detail. An employer can offer a salary well above the Level I floor and still get flagged, because the *prevailing wage* for the occupation is calculated at Level I under DOL's own formula. The petition then has to prove, with expert letters and industry data, that an entry-level wage is appropriate for a job whose duties were written to impress — words like "lead," "design strategy," "architect," or "manage" become liabilities. Fragomen, one of the largest immigration firms, reports RFEs hitting cap cases and routine extensions alike, with denials rising above prior years.

## Why Indians absorb the brunt

Two structural facts make this an India story. First, volume: Indian nationals receive the majority of H-1B approvals, so any tightening of adjudication standards lands disproportionately on them by sheer arithmetic. Second, the profile. A large slice of Indian H-1B workers are early-career engineers and data professionals placed through IT services and staffing firms — exactly the entry-level, Level I-wage profiles that draw the most scrutiny.

There is a second front. Bloomberg Law reports that EB-2 National Interest Waiver petitions — long a favored green card route for Indian researchers and specialists stuck in the backlog — are seeing the same treatment: longer delays, tougher RFEs, unexpected denials. The two pressure points compress the diaspora from both ends, the temporary visa and the permanent one.

And there is the strangest twist of all: AI. Several law firms note that USCIS appears to be using automated systems to flag petitions with reused or "drop-in" digital signatures — the kind generated by Adobe or copied across filings. A petition can now be delayed not for any substantive flaw but because the form was signed with the wrong tool.

## What it means in practice

For the worker, the consequences are concrete. An RFE adds months of uncertainty to a case. A denial on an extension can leave someone out of status, triggering the 60-day clock to find a new sponsor or leave. For families, it freezes plans — a home purchase, a child's school enrollment, a spouse's H-4 work permit that rides on the primary visa.

The defensive playbook, per the firms handling these cases, is unglamorous but effective. Align the wage level with the job duties before filing: if the role is classified at Level I, describe it as supervised and foundational, not strategic. Avoid senior-sounding verbs in petitions for entry-level wages. Build the evidentiary record up front — expert opinions, salary surveys, detailed duty breakdowns — rather than waiting for the RFE to demand them. And use original or stylus signatures, not reused digital stamps, to stay clear of the AI flags.

## The bigger picture

None of this is announced in a press release. There is no proclamation to challenge in court, no single rule to enjoin. That is precisely what makes it durable. A $100,000 fee can be struck down in a week; an adjudication culture that treats every entry-level petition as suspect cannot be litigated away. For Indian professionals weighing whether the H-1B is still a reliable path, the quiet RFE may say more about the next few years than the headline fee ever did."""

article3_body = """The cost of becoming an American is about to jump by three-quarters, and Indians are standing at the front of the line that will feel it. A Department of Homeland Security proposal published this week in the Federal Register would raise the fee for the N-400 naturalization application from $760 to $1,330 for a paper filing — a 75 percent increase — and from $710 to $1,280 for filing online, an 80 percent jump. Appeal fees climb even more steeply, and the low-income fee waivers that many applicants rely on would be eliminated.

For a diaspora that treats citizenship as the long-delayed reward at the end of a green card marathon, the timing could hardly be worse.

## What is changing

The numbers, drawn from the proposal as reported by CBS News, Newsweek and Mint, are blunt:

- Paper N-400: $760 to $1,330 (up 75%)
- Online N-400: $710 to $1,280 (up 80%)
- Paper N-336 appeal: $830 to $1,475 (up 78%)
- Online N-336 appeal: $780 to $1,425 (up 83%)

DHS frames the increase as cost recovery. The agency says the higher fees are needed to fund the "expanded screening and vetting requirements" ordered under recent executive actions, and argues that naturalization — "the most significant immigration benefit" — should pay its full freight rather than be subsidized. Officials acknowledged in the filing that the change "could delay applications for many legal permanent residents" and would discourage some people from applying at all.

The proposal also drops a long-standing principle. DHS wrote that it "no longer believes naturalization benefit requests should get lower fees at the potential expense of other immigration benefits" — a quiet reversal of decades of policy that kept citizenship deliberately affordable to encourage integration. Fee waivers would survive only for one group: those naturalizing through military service.

The rule carries a 60-day public comment period before DHS can finalize it.

## Why Indians are at the front of the line

India sits among the top origin countries for new American citizens, and the structural reason is the green card backlog. Because EB-2 and EB-3 wait times for Indians stretch past a decade, a vast cohort of Indian professionals has been holding permanent residency for years, becoming eligible to naturalize in overlapping waves. When a fee rises, that cohort absorbs it in disproportionate numbers — roughly ₹1.26 lakh now for a single paper application, before legal help or biometrics.

The increase also collides with a second pressure the diaspora is already weighing. This week's Supreme Court ruling in *Blanche v. Lau* made a green card more fragile at the border, lowering the evidence a CBP officer needs to parole a returning resident with any criminal history. The lesson immigration attorneys keep repeating — that citizenship is the only status the government cannot pause at an airport — has never been more pointed. DHS is raising the price of that protection at the exact moment its value is rising.

## The squeeze on lower-income applicants

The elimination of fee waivers is the sharpest edge. Naturalization has long been within reach for working-class permanent residents precisely because USCIS waived fees for those who could not pay. Strip that away and the door narrows for a slice of the community — service workers, caregivers, small-business families — who are eligible to naturalize but cannot easily find $1,330 plus the cost of an attorney. Critics cited by Mint argue the change will disproportionately keep lower-income immigrants in permanent-resident limbo, the very status the Supreme Court just made riskier.

## What to do with the comment window

The 60-day period before the rule is finalized is not a formality; it is the only lever the public has. Comments submitted to the Federal Register become part of the record DHS must address, and immigration advocacy groups are expected to mobilize filings during the window.

For individuals, the practical calculus is simpler. Anyone already eligible to naturalize — five years as a permanent resident, or three if married to a citizen — has a financial reason to file before the rule takes effect, locking in the current $760 or $710 fee. For those relying on a waiver, the window may be the difference between applying at all and waiting indefinitely. The marathon, for many Indians, is about to get a toll booth at the finish line. The time to cross is now."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Charge Is Now Enough: The Supreme Court Just Made Every Indian Green Card More Fragile at the Border",
        "subheadline": "In a 6-3 ruling, the justices freed border officers to treat returning permanent residents as outsiders on a pending charge — no conviction required. For a diaspora that holds green cards for a decade, the airport line just got riskier.",
        "slug": make_slug("blanche-lau-supreme-court-green-card-border-charge-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Most Indians in the US hold green cards for a decade-plus while stuck in the EB-2/EB-3 backlog, and Blanche v. Lau means any old or pending charge can now strip that status at the airport on return from India.",
        "tags": ["green card", "supreme court", "lpr", "deportation", "blanche v lau", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/news/justice/clarence-thomas-dhs-green-card-blanche-lau"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/us-law-week/justices-back-border-officers-in-dispute-over-green-card-reentry"},
            {"name": "Legal Information Institute (Cornell Law)", "url": "https://www.law.cornell.edu/supremecourt/text/25-429"},
            {"name": "Daily Caller", "url": "https://dailycaller.com/2026/06/23/supreme-court-trump-green-card-holders-blanche-lau/"}
        ]),
        "score_total": 86,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Exterior_of_Supreme_Court_Building_20240601.jpg/1280px-Exterior_of_Supreme_Court_Building_20240601.jpg",
        "image_caption": "Exterior of the United States Supreme Court Building in Washington, D.C., where Blanche v. Lau was decided on June 23, 2026",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Forget the $100,000 Fee. The Wage-Level RFE Is the H-1B Threat Quietly Hitting Indians Hardest",
        "subheadline": "USCIS is flagging entry-level petitions whose job descriptions sound too senior for their wage tier — and Indian engineers, who fill most H-1B slots, are absorbing the surge in Requests for Evidence and denials.",
        "slug": make_slug("h1b-wage-level-rfe-surge-uscis-denials-indians-niw"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals receive the majority of H-1B approvals and dominate the entry-level, Level I-wage profiles now drawing the most RFEs and denials, so the quiet adjudication crackdown lands on them far more than the headline fee fight.",
        "tags": ["h1b", "uscis", "rfe", "wage level", "niw", "eb2", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen", "url": "https://www.fragomen.com/insights/h-1b-processing-update-tougher-scrutiny.html"},
            {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/us-law-week/how-to-strengthen-worker-visa-applications-amid-growing-scrutiny"},
            {"name": "Dickinson Wright", "url": "https://www.dickinson-wright.com/news-alerts/rising-scrutiny-in-employment-based-visas"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A US visa application and passport on a desk, the paperwork at the center of rising H-1B Requests for Evidence",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": article2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Price of Becoming American Is Jumping 75% — and Indians Are at the Front of the Line",
        "subheadline": "A new DHS proposal would push the naturalization fee from $760 to $1,330 and scrap low-income waivers. For a diaspora stuck in green-card limbo for years, the cost of the only status safe at the border just spiked.",
        "slug": make_slug("n400-citizenship-fee-hike-75-percent-waivers-indians-naturalization"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is among the top origin countries for new US citizens because of the decade-long green-card backlog, so a 75% N-400 fee hike and the end of fee waivers hit the large Indian cohort eligible to naturalize harder than almost any other group.",
        "tags": ["naturalization", "n400", "citizenship", "uscis", "fee hike", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy-and-policy/us-citizenship-fee-hike-indian-green-card-holders"},
            {"name": "USA Today", "url": "https://www.usatoday.com/story/news/politics/2026/06/23/trump-citizenship-fee-increase-naturalization/"},
            {"name": "CBS News", "url": "https://www.cbsnews.com/news/citizenship-application-fee-increase-naturalization-dhs/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/9/96/Centennial_Naturalization_Ceremony_%2828980411545%29.jpg/1280px-Centennial_Naturalization_Ceremony_%2828980411545%29.jpg",
        "image_caption": "New citizens take the Oath of Allegiance at a US naturalization ceremony",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": article3_body,
    },
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}  ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
