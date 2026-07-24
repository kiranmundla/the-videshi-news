#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

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
        "headline": "A Court Killed the $100,000 H-1B Fee. Congress Is Trying to Resurrect It as Law",
        "subheadline": "A federal judge struck down Trump's six-figure visa surcharge as an illegal tax. Now Rep. Mike Kennedy wants Congress to make it permanent — beyond the reach of any court.",
        "slug": make_slug("protect-act-kennedy-codify-100k-h1b-fee-congress-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians win roughly 70% of H-1B visas, so a $100,000 fee written into permanent statute would fall hardest on Indian professionals and the firms that sponsor them.",
        "tags": ["h1b", "100k-fee", "protect-act", "congress", "uscis", "legislation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Daily Caller News Foundation", "url": "https://dailycaller.com/2026/06/10/mike-kennedy-protect-act-h1b-fee-sorokin-ruling/"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/100000-h-1b-visa-fee-us-judge-blocks-lawmakers-cheer-and-trump-lambasts/"},
            {"name": "NBC Palm Springs", "url": "https://nbcpalmsprings.com/2026/06/15/federal-judge-blocks-100000-fee-on-h-1b-visa-applications/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/20417783/pexels-photo-20417783.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The United States Capitol in Washington, where the fight over the H-1B fee has shifted from the courts to Congress",
        "image_attribution": "Pexels",
        "body": """The $100,000 H-1B fee that sent Indian tech workers and their employers into a year of anxiety was supposed to be dead. On Monday, U.S. District Judge Leo Sorokin struck it down, ruling that the Trump administration had no power to impose what amounted to a six-figure tax on visa petitions. Only Congress, he held, can levy a tax of that kind — and Congress never authorized this one.

The relief lasted about a day.

Within twenty-four hours, Republican Rep. Mike Kennedy of Utah was promoting the PROTECT Act, a bill designed to do precisely what the court said the executive branch could not: write the $100,000 fee into permanent federal law. "We needed somebody in Congress to actually take care of this," Kennedy told the Daily Caller News Foundation. His bill would require any H-1B applicant to pay the greater of the prevailing wage or a $100,000 base, and it would pressure companies to exhaust American hiring before reaching for foreign talent.

The legal logic of Sorokin's ruling is what makes the legislative pivot so significant. The judge, citing the Supreme Court's tariff decision from February, concluded that the substance of the payment — not its label — revealed it to be a tax. Article I of the Constitution reserves taxation to Congress. That reasoning leaves one obvious workaround: if the problem is that the president acted without congressional authority, then a statute passed by Congress cures the defect. The PROTECT Act is that cure.

## A whipsaw with no good exit for Indians

For Indian professionals, the past nine months have been an exercise in legal whiplash. Trump's September 2025 proclamation introduced the fee. A Washington, D.C. judge initially upheld it. Then the Supreme Court's tariff ruling shifted the ground, and Sorokin voided it. Now the question is whether what a court took away, a legislature will hand back — this time with no judicial off-ramp.

The stakes are not abstract. Indians win roughly 70 percent of H-1B visas in a typical year. A fee that survives as statute would not be a temporary policy that the next administration could reverse with a stroke of a pen. It would be the law of the land, and overturning it would require a future Congress to act.

The fee, crucially, applies to new petitions for workers filed from outside the United States. Professionals already inside the country on eligible status — F-1 students changing to H-1B, for instance — have generally been treated as exempt. That distinction has quietly reshaped strategy. Indian graduates of American universities now hold a structural advantage over equally qualified engineers sitting in Bengaluru or Hyderabad, because the latter group is the one the fee was built to price out.

## The offshoring math writes itself

Employers have already done the arithmetic. A staffing firm weighing whether to bring an engineer onshore at a six-figure surcharge or keep the work in an Indian delivery center reaches an obvious conclusion. The fee does not just tax the visa; it tilts the entire economics of global tech labor toward offshore and nearshore models that Indian IT majors have spent years building anyway.

That is part of why the policy debate has grown so charged. Supporters like Kennedy frame the fee as protection for American white-collar workers. Critics counter that it functions as a wall against precisely the high-skilled immigration that built much of Silicon Valley — and that India has supplied in disproportionate numbers.

## What to watch next

The PROTECT Act faces a long road. Codifying a $100,000 fee is a heavy legislative lift, and any bill will draw fierce opposition from the technology industry, universities, and immigration advocates. But the mere existence of the effort changes the calculus for anyone planning an H-1B filing.

The lesson of the past week is that a court victory is no longer the end of the story. For Indian families weighing whether to bet a career on the American work-visa system, the relevant question is no longer just what the agencies decide — it is what Congress might pass. And on that front, the fee that a judge declared illegal on Monday was, by Tuesday, back on the table."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Quiet Rule Change That Could Put a Four-Year Clock on Every Indian Student in America",
        "subheadline": "DHS wants to scrap the 'duration of status' framework that has let international students stay as long as they study. For Indians counting on OPT and repeated H-1B tries, the flexibility that made the gamble worthwhile is on the chopping block.",
        "slug": make_slug("dhs-duration-of-status-f1-fixed-four-year-opt-cpt-indians"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest international student groups in the US and lean heavily on OPT, CPT and the H-1B lottery; a fixed four-year admission term would squeeze the very flexibility that makes a US degree a viable path to a career.",
        "tags": ["f1-visa", "opt", "cpt", "students", "dhs", "duration-of-status"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "ANI / Industries News", "url": "https://engineering.industriesnews.net/tighter-student-visa-rules-may-deepen-ai-talent-shortage-in-us"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/tighter-student-visa-rules-may-impact-indians-in-us-expert/"},
            {"name": "Collegedunia", "url": "https://collegedunia.com/news/indian-opt-students-travelling-home-summer-f1-visa-stamp"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7942484/pexels-photo-7942484.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International graduates at a US university commencement, a pipeline that increasingly runs through the H-1B lottery",
        "image_attribution": "Pexels",
        "body": """For decades, an international student in the United States lived under a forgiving piece of immigration bureaucracy called "duration of status." As long as you kept studying, complied with the rules, and held valid enrollment, you could stay. There was no expiry date stamped on your welcome — only the open-ended permission to remain a student.

The Department of Homeland Security wants to end that. A rule proposed on May 5, 2026 would scrap duration of status for F-1 visa holders and replace it with a fixed admission period of up to four years. Any stay beyond that — a PhD that runs long, a medical program, or post-graduation work authorization — would require formal approval from U.S. Citizenship and Immigration Services. The open-ended welcome would become a countdown.

For Indian students, who form one of the two largest international cohorts in the country, this is not a technical footnote. It is a structural threat to the entire calculation that brings tens of thousands of them to American campuses each year.

## Why the flexibility mattered

The appeal of a U.S. degree for an Indian student was never just the diploma. It was the runway it bought. After graduation, Optional Practical Training (OPT) allows up to a year of work — three years for STEM graduates — and that window is what students use to enter the H-1B lottery, often across multiple annual cycles. When the lottery does not break their way, many enroll in another program and use "Day 1 CPT" to keep working legally while they try again.

That whole ecosystem runs on flexibility — the ability to extend, switch programs, and stay in valid status through a university rather than a federal adjudication queue. Danielle Goldman, co-founder and CEO of the immigration platform Build, put it bluntly: the proposed rule "is going to fundamentally change the flexibility that students have had to apply for Optional Practical Training and Curricular Practical Training."

Under a fixed four-year term, every extension becomes a USCIS decision rather than a school's call. And USCIS adjudications are slow, discretionary, and increasingly inclined toward Requests for Evidence. A student who would once have rolled smoothly from one program into another could find themselves waiting on a federal officer's signature, with their legal status hanging on the timeline.

## The second cut: a shorter grace period

The proposal carries a quieter sting. Goldman also flagged a plan to halve the grace period after F-1 status ends — from 60 days to 30. For a graduate who has just missed the H-1B lottery, that compressed window may not be enough time to find a sponsoring employer, file a change of status, or arrange an orderly exit. Thirty days is not a runway; it is a cliff edge.

The "Day 1 CPT" route, already legally contested, would narrow sharply. Goldman noted that someone who already holds a master's degree cannot simply enroll in another master's program to manufacture work authorization. For thousands of Indians in AI, machine learning, software engineering, and data science — fields where repeated H-1B rejection is common — that escape hatch could close.

## The talent-shortage irony

The sharpest critique of the proposal is that it may injure the very sector it claims to protect. Goldman warned that tighter student rules could deepen an AI talent shortage, because the international graduates being squeezed are disproportionately the ones filling specialized technical roles American universities cannot staff from the domestic pool alone.

For Indian students weighing a U.S. education right now, the message is unsettling. The degree may still be world-class. But the path from campus to career — the part that justified the tuition and the distance from home — is being rewired in ways that make the outcome far less certain. A four-year clock changes the bet entirely, and it is Indian students, more than almost any other group, who placed the most chips on the old rules."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "ICE Found Locked, Empty Buildings Where OPT Workers Were Supposed to Be. Now the Program Itself Is the Target",
        "subheadline": "A federal crackdown on Optional Practical Training fraud has exposed phantom worksites and shell employers. The fallout threatens a work pathway that Indian graduates rely on more than anyone.",
        "slug": make_slug("opt-fraud-crackdown-ice-phantom-worksites-indian-students-stem"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "OPT and STEM OPT are the bridge Indian graduates use between a US degree and the H-1B lottery; a fraud crackdown that fuels calls to abolish the program puts that bridge — and the legitimate majority who use it — at risk.",
        "tags": ["opt", "stem-opt", "ice", "fraud", "f1-visa", "students"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Center for Immigration Studies", "url": "https://cis.org/Arthur/OPT-Foreign-Student-Work-Program-End-It-Dont-Mend-It"},
            {"name": "ANI / Industries News", "url": "https://engineering.industriesnews.net/tighter-student-visa-rules-may-deepen-ai-talent-shortage-in-us"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/17057647/pexels-photo-17057647.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An empty office interior; ICE investigators reported finding vacant worksites listed as employment for hundreds of OPT workers",
        "image_attribution": "Pexels",
        "body": """The investigators went looking for jobs and found ghosts. Locked, empty buildings where hundreds of Optional Practical Training workers were supposedly employed. Small private homes listed as worksites for hundreds of people. Multiple "employers" sharing a single address. Acting ICE Director Todd Lyons, describing the findings at a press conference this week, called it "only the tip of the iceberg" — and noted that investigators had examined just the top 25 employers of OPT workers.

The crackdown has handed ammunition to a long-running campaign to abolish OPT entirely, and that is the part Indian graduates should be watching closely. Because for them, OPT is not a peripheral perk. It is the bridge.

## What OPT does, and why Indians depend on it

Optional Practical Training lets graduates of U.S. universities work for up to a year in a field related to their studies — extended to three years for STEM graduates. That work window is precisely the period during which a graduate enters the H-1B lottery, usually across several annual cycles, hoping one of them lands. Without OPT, the gap between graduation and a work visa would be unbridgeable for most. The degree would lead nowhere.

Indians, who make up one of the largest international student populations in the country and a disproportionate share of H-1B applicants, are the heaviest users of this pathway. When critics talk about ending OPT, they are talking about removing the single mechanism that turns an Indian student's American education into an American career.

## The fraud is real — and so is the overreach risk

There is no honest way to dismiss the abuse ICE uncovered. Phantom worksites and shell employers are fraud, full stop, and they damage the credibility of every legitimate participant. The Center for Immigration Studies, a longtime OPT opponent, seized on the findings to argue that the program is "a magnet for fraud" that should be ended rather than reformed. Vice President JD Vance has spotlighted fraud enforcement more broadly, and the OPT revelations slot neatly into that narrative.

But the framing carries a familiar danger for the diaspora: collective punishment. The overwhelming majority of OPT participants are graduates working real jobs at real companies, paying taxes, and waiting out the H-1B lottery. A crackdown that morphs into abolition would not separate the fraudsters from the honest workers. It would sweep away both.

## A program caught in a wider squeeze

The OPT investigation does not stand alone. It arrives alongside a DHS proposal to scrap the "duration of status" framework for F-1 students and impose a fixed four-year admission term — a change that would itself narrow OPT and CPT flexibility. Layer the fraud crackdown on top, and the cumulative effect is a student-to-work pipeline being constricted from several directions at once.

For an Indian student currently on OPT, or planning to rely on it, the immediate risk is not deportation — it is uncertainty. Heightened scrutiny means more verification, more documentation demands, and more pressure on employers to prove that worksites and roles are genuine. Legitimate workers may find themselves answering for a system's failures they had no part in creating.

## The bottom line

ICE deserves credit for exposing genuine corruption, and the people running fake worksites should face consequences. But the longer-term question is the one Indian graduates cannot afford to ignore: will this become the first step toward dismantling OPT, or a targeted cleanup that preserves the pathway for those using it honestly?

The answer will shape whether a U.S. STEM degree remains a viable route to a U.S. career — or becomes an expensive credential with no bridge to the other side. For the tens of thousands of Indians who bet on that bridge, the difference is everything."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"OK {art['slug']}")
    except Exception as e:
        print(f"FAIL {art['slug']}: {e}")
