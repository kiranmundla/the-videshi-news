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

article1_body = """The green card was supposed to be the escape hatch. For Indian professionals staring down an EB-2 backlog measured in decades, the self-petition categories — EB-1A for "extraordinary ability" and the EB-2 National Interest Waiver — offered a way to skip the employer-sponsored queue and, in the EB-1A's case, a shorter line entirely. No PERM labor certification, no employer to anchor you, just your own record of achievement. Over the past three years, tens of thousands of Indian engineers, researchers and founders rebuilt their immigration strategy around these two doors.

Both are now closing.

## The numbers tell the story

USCIS adjudication data shows a category that has quietly transformed. The EB-1A — the "Einstein visa" — approved petitions at rates near 80% just a few years ago. By the fourth quarter of FY2025, the approval rate had fallen to 53.4%. Put plainly: a petition filed today is closer to a coin flip than a sure thing.

The EB-2 NIW collapsed harder and faster. Its approval rate dropped from roughly 80% in FY2023 to 43.31% in FY2024 — meaning the supposedly more flexible category is now being denied *more often* than the elite EB-1A. For a cohort of Indian applicants who were told NIW was the pragmatic, lower-risk play, that reversal is jarring.

By contrast, EB-1B (outstanding researchers) and EB-1C (multinational managers) continued approving above 96%. The squeeze is specific and deliberate: it falls on the categories where an individual vouches for themselves, not where an employer and the PERM process have already validated the role.

## Where the denials come from

Adjudicators have not, for the most part, rewritten the rules. They have changed how the existing two-step *Kazarian* framework is applied. Step one is a mechanical count — does the record satisfy at least three of ten regulatory criteria? Most petitioners still clear it. Step two is the "final merits determination," a holistic judgment about whether the evidence, taken together, shows sustained acclaim placing the applicant at the very top of their field.

Step two is where 2026 denials are manufactured. Officers increasingly approve at the criteria-count stage and then deny at final merits, writing that the evidence "does not, in the aggregate, demonstrate sustained acclaim." That single sentence now appears in denial after denial, across professions and service centers. It is nearly impossible to litigate against, because it is a discretionary conclusion rather than a missing document.

## Why this lands hard on Indians

No group leans on these categories the way Indian nationals do, and for a structural reason: the EB-2 and EB-3 employer-sponsored lines for India are so backlogged that the wait stretches well beyond a working career. EB-2 India went fully unavailable in this fiscal year. EB-5 ran dry. When the conventional employment-based doors freeze, the self-petition categories become the only ones offering forward motion — which is exactly why Indian filings concentrated there.

That concentration created its own backlash. As volume surged, scrutiny rose. The applicants most dependent on a working escape hatch are now the most exposed to its tightening.

## What practitioners are advising

The shift does not make these petitions hopeless — it makes preparation decisive. Immigration attorneys tracking the trend converge on a few points:

- **Front-load the evidence.** A petition that wins at final merits reads as overwhelming on first pass. Independent expert letters, citation metrics, documented economic or scientific impact, and third-party recognition matter more than criteria-checking boxes.
- **Show measurable U.S. impact.** Citations, job creation, revenue, adoption — quantified influence is what survives the final-merits test.
- **Treat premium processing carefully.** Paying $2,805 buys speed, but several practitioners report it can correlate with higher RFE rates, not lower. Speed is not the same as strength.
- **Keep the H-1B alive.** With both self-petition doors narrowing, abandoning nonimmigrant status to bet everything on EB-1A is riskier than it was a year ago.

The "Einstein visa" was never meant to be a mass pathway. For a community boxed in by a generational green card backlog, it became one anyway. The data now says that improvised exit is being narrowed — and that the strongest, best-documented cases are the only ones likely to make it through."""

article2_body = """A man with a cigarette in his mouth tore an Indian flag outside Frisco City Hall while a crowd cheered. The video, filmed at an immigration-related protest in the fast-growing Dallas suburb, spread across social media within hours. Days later, six Indian American members of Congress issued a joint statement — and in doing so turned a local incident into a national marker of how the immigration debate is curdling into something more personal for the diaspora.

## What happened

The footage shows a Texas resident, identified in reports as Clayton Walker, ripping the Indian tricolor as anti-India slogans rose from the crowd. The clip was captioned with profanity directed at India and framed around anger over "Indian immigration" into north Dallas. Walker later said he had received threatening messages and defended the act as protected free speech: "All I did was exhibit my right to freedom of speech as an American."

The setting matters. Frisco's Asian population — overwhelmingly Indian — has climbed to roughly a third of the city, driven by tech-sector growth and H-1B hiring. That demographic shift has surfaced repeatedly at city council meetings, some of which have featured speakers warning of an "Indian takeover." The flag-tearing did not come from nowhere; it sits on top of months of escalating local rhetoric.

## The congressional response

On June 16, Representatives Raja Krishnamoorthi, Ami Bera, Pramila Jayapal, Ro Khanna, Shri Thanedar and Suhas Subramanyam — every Indian American member of the U.S. House — released a joint statement. They drew a careful line between protected speech and targeted hate.

"We strongly support the constitutional right to freedom of expression for all Americans," the statement read. "At the same time, we condemn the tearing of an Indian flag outside Frisco City Hall alongside hateful anti-India rhetoric, which continues to fuel anti-Indian violence and xenophobia."

They went further, naming the underlying fear directly: "The Indian American community is an important part of our nation and deserves to feel safe and respected. As Indian Americans and South Asian Americans face harassment, xenophobia, and hateful rhetoric, leaders must speak clearly: hate targeting any community cannot be tolerated or ignored."

That six lawmakers from both parties' orbits — progressives like Jayapal and Khanna alongside more centrist figures like Bera and Subramanyam — chose to speak with one voice signals how seriously the community's elected representatives are treating the moment.

## Why this matters to the diaspora

For a community that has largely measured its American story in professional achievement — H-1B to green card to citizenship, suburb to good schools — incidents like Frisco puncture an assumption: that economic contribution buys belonging. The flag is a symbol, but the anxiety it triggered is concrete. A March 2026 analysis found anti-Indian content on social media tripled in 2025, frequently spiking in sync with federal immigration policy changes such as the new H-1B fee.

The timing compounds the unease. The diaspora is already absorbing a year of tightening: frozen green card categories, a contested $100,000 H-1B fee, longer consular waits, shorter work permits. Against that backdrop, a public act of hostility in a city that is one-third Indian reads less like an isolated outburst and more like a temperature reading.

## The harder conversation

The lawmakers were deliberate in protecting the right to protest immigration policy. The distinction they drew — policy disagreement is legitimate, ethnic targeting is not — is the one the community itself has pressed online, where many commenters pointed to Indian American economic contributions while insisting the debate stay focused on policy rather than people.

Whether that line holds is the open question. Frisco's council meetings suggest the rhetoric around demographic change is not receding, and national policy continues to keep Indian immigration in the headlines. For Indian American families weighing where to raise children and build careers, the episode is a reminder that the climate they live in is shaped not only by visa bulletins and USCIS memos, but by what their neighbors feel free to say — and do — in front of a cheering crowd."""

article3_body = """The fee gets the headlines. The denial gets the worker. While the immigration world has fixated on the contested $100,000 H-1B charge, a quieter mechanism has been doing more day-to-day damage to early-career Indian techies: the Request for Evidence aimed at entry-level wages. It is bureaucratic, it is technical, and it is reshaping who gets to start a career in America.

## The Level 1 trap

Here is how it works. The Department of Labor sorts prevailing wages into four levels, with Level 1 representing entry-level roles requiring close supervision. New graduates — including the enormous cohort of Indian students moving from F-1 and OPT into their first H-1B job — are frequently slotted at Level 1, because that is genuinely what their roles are.

USCIS has increasingly treated a Level 1 wage as a red flag. Adjudicators issue RFEs arguing that if a position pays at the entry level, it cannot be complex enough to qualify as a "specialty occupation" demanding a bachelor's degree. The logic is circular — the job is too junior to need a degree, yet H-1B by definition requires one — but the burden lands on the employer to disprove it.

Immigration firms report these RFEs surging even when the offered salary far exceeds the Level 1 floor, because the prevailing-wage *calculation* still anchors to Level 1. Employers must now produce expert opinions, industry data and detailed duty breakdowns simply to defend hiring a new graduate at a normal starting role. For a startup or a smaller firm, that paperwork burden is often enough to make sponsoring a fresh grad not worth it.

## The wording adjudicators use

The pattern is consistent. An RFE will claim the job duties "appear too complex" for a Level 1 wage, or that the Level 1 designation "suggests the position does not qualify as a specialty occupation," or both at once. Practitioners describe a no-win framing: describe the role as substantive and USCIS says it is too senior for Level 1; describe it as entry-level and USCIS says it is too simple to require a degree.

The guidance that flows from this is counterintuitive but important. Attorneys now warn employers to avoid senior-sounding language — "lead," "supervise," "design strategy," "invent" — in any Level 1 petition, and to make sure the wage level and the written duties tell a single, consistent story. Misalignment between the two is the single most common RFE trigger.

## The job-change trap on top of it

For Indians already in the system, a second hazard compounds the first. Workers who get laid off, bridge to a B-2 visitor status while job-hunting, and then have a new employer file a fresh H-1B are increasingly hitting paired RFEs — one challenging the B-2, one challenging maintenance of status. The frequent outcome is an H-1B "approved with consular notification": USCIS accepts the job and the worker but rejects the claim that status was maintained inside the U.S.

The consequence is brutal for Indian nationals specifically. Approval with consular notification means the visa cannot be activated from within the country — the worker must depart and get a new stamp abroad. And Indians, unlike many other nationalities, generally cannot shop for third-country interview slots; they must interview in India, where wait times stretch for months. A footnote on an approval notice can cost a year and, potentially, expose the new petition to the $100,000 fee.

## Why Indians absorb the worst of it

The math is structural. Indian nationals account for roughly 71% of H-1B beneficiaries, and the F-1-to-OPT-to-H-1B pipeline is overwhelmingly Indian. The workers most affected by Level 1 RFEs are precisely those at the start of that pipeline — new graduates with strong degrees but no seniority, taking normal entry-level offers. They are the demographic the specialty-occupation challenge hits hardest.

The practical advice from practitioners is unglamorous but vital: maintain status documentation meticulously — I-94s, prior approvals, pay records, travel history; align wage level and job duties before filing; and never assume deference will carry an extension. In 2026, the small print is where careers are made or broken — and for early-career Indian professionals, it is the part of the system that has quietly turned most hostile."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Green Card Escape Hatch Indians Built Is Quietly Sealing Shut",
        "subheadline": "EB-1A and NIW approval rates have collapsed just as India's employer-sponsored green card lines froze — leaving the diaspora's last forward-moving pathway under the tightest scrutiny in years.",
        "slug": make_slug("eb1a-niw-einstein-visa-denial-collapse-india-self-petition"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians, boxed in by a decades-long EB-2/EB-3 backlog, leaned hardest on the EB-1A and NIW self-petition categories — exactly the doors whose approval rates are now collapsing.",
        "tags": ["eb1a", "niw", "green-card", "uscis", "immigration", "india"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "VisaVerge — EB-1A Processing Times and Approval Rates 2026", "url": "https://www.visaverge.com/"},
            {"name": "Manifest Law — EB-2 NIW Denials Now Outpace EB-1A: Recent USCIS Trends", "url": "https://www.manifestlaw.com/"},
            {"name": "AILA — A Little about that 'Einstein' Visa", "url": "https://www.aila.org/"}
        ]),
        "score_total": 82,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An immigration applicant reviews visa and green card paperwork at a desk",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Torn Flag in Frisco, and Six Lawmakers Who Decided It Wasn't Local Anymore",
        "subheadline": "Every Indian American member of Congress condemned the flag-tearing outside Frisco City Hall — a sign of how sharply the immigration debate is turning personal for a diaspora that is now a third of the city.",
        "slug": make_slug("frisco-indian-flag-tearing-congress-condemn-xenophobia-diaspora"),
        "category": "immigration",
        "vertical": "diaspora-safety",
        "diaspora_angle": "For a community that measured belonging in professional achievement, a public act of hostility in a city that is one-third Indian is a temperature reading on how welcome the diaspora actually feels.",
        "tags": ["diaspora", "xenophobia", "frisco", "texas", "indian-americans", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Rep. Krishnamoorthi — Joint Statement on Frisco Demonstration", "url": "https://krishnamoorthi.house.gov/"},
            {"name": "Mint — Texas man tears Indian flag as crowd cheers", "url": "https://www.livemint.com/"},
            {"name": "India-West — Indian Flag Torn at Texas Protest Sparks Backlash", "url": "https://www.indiawest.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8181770/pexels-photo-8181770.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The United States Capitol in Washington, where Indian American lawmakers issued their joint statement",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B's Quietest Weapon Against New Indian Grads Isn't the Fee — It's the Level 1 Wage",
        "subheadline": "USCIS is treating entry-level salaries as proof a job isn't a 'specialty occupation,' triggering a surge of Requests for Evidence that hits the F-1-to-OPT-to-H-1B pipeline hardest.",
        "slug": make_slug("h1b-level-1-wage-rfe-specialty-occupation-new-grads-india"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "New Indian graduates moving from OPT into their first H-1B job are exactly the cohort slotted at Level 1 wages — and exactly the cohort USCIS's specialty-occupation RFEs now target most.",
        "tags": ["h1b", "rfe", "opt", "uscis", "specialty-occupation", "india"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Fragomen — H-1B Processing Update: Tougher Scrutiny, Adjudication Delays", "url": "https://www.fragomen.com/"},
            {"name": "Bloomberg Law — How to Strengthen Worker Visa Applications Amid Growing Scrutiny", "url": "https://news.bloomberglaw.com/"},
            {"name": "American Bazaar — How to prepare for H-1B success amid rising fees, RFEs, scrutiny", "url": "https://www.americanbazaaronline.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6804068/pexels-photo-6804068.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A software engineer works at a computer in an office setting",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"   words={wc} slug={art['slug']}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
