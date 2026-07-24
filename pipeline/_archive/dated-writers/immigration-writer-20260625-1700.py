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

body1 = """The numbers keep getting worse, and they keep landing on the same people. U.S. consulates in India are now quoting waits of 75 to more than 125 days for an employment-based nonimmigrant visa appointment — the H and L stamps that keep Indian tech careers running. The figures come from immigration firm Fragomen's latest tracking, and the trajectory is the story: the backlog is not stabilizing, it is spreading.

## The last cheap door just closed

For months, the workaround whispered through H-1B WhatsApp groups was Kolkata. The consulate there carried an appointment backlog of just 13 days, a rounding error next to the multi-month queues at Chennai, Hyderabad, Mumbai and New Delhi. That door is now shut. Kolkata's wait has ballooned to 126 days since late August, putting it in line with every other post in the country.

The cause is not mysterious. Demand for U.S. visas has climbed steadily over the past several months while consular staffing in India has not budged. Layer on the State Department's expanded "online presence" review — officers must now examine the social-media footprints of H-1B and H-4 applicants before issuing — and each interview simply takes longer. Fewer interviews per day, against rising demand, produces exactly the math now staring back at applicants.

## Why an Indian engineer should care more than anyone

This is not an abstract processing statistic. For an Indian national on H-1B, a visa stamp is the difference between a routine trip home and a career-threatening gamble. The stamp inside the passport is what permits re-entry; if it has expired, the worker cannot return to the United States until a consulate issues a new one. A 125-day backlog means a two-week visit to see parents in Pune can metastasize into four months stranded abroad — long enough to lose a job that an employer cannot legally hold vacant, and that often cannot be performed remotely from outside the country because of payroll, tax and export-control rules.

The H-4 dimension makes it harder. Spouses and children stamp at the same posts, on the same timelines. A family that travels together risks being separated from work, school and home for a third of a year.

## The third-country escape hatch is narrowing

The traditional pressure valve — applying as a third-country national (TCN) at a U.S. consulate outside India, often in Canada, Mexico or the Gulf — still exists, but it is no bargain. It means buying flights, sometimes securing a visa for the third country itself, and gambling that the officer there will accept a non-resident applicant at all. Some posts have grown wary of TCN H-1B volume. For families, the cost multiplies by every passport.

## What to actually do

The practical advice from immigration counsel has hardened into a single rule: do not leave the United States for stamping unless you absolutely must. If your visa stamp is still valid, travel is fine. If it has expired, treat any international trip as a months-long commitment and plan the absence accordingly — or defer it.

For those who must stamp, the levers are small but real. File the DS-160 the moment a petition is approved, pay the MRV fee immediately, and check the appointment portal obsessively; cancellations open slots that vanish within minutes. Keep documentation airtight, because an administrative-processing flag (a 221(g)) on top of a 125-day queue can stretch the timeline past a year. And scrub nothing, but be aware that the social-media review is now a formal step, not a rumor.

## What's next

There is no quick fix on the horizon. Adding consular officers takes months of clearance and training, and there is no public signal that the U.S. mission to India is expanding capacity. India's government has raised the appointment delays with Washington, citing the hardship to applicants, but a diplomatic note does not shorten a queue.

For the roughly two million H-1B and H-4 Indians whose lives run on the validity dates inside their passports, the message for the rest of 2026 is unglamorous but clear: stay put, plan early, and assume the line is longer than it was yesterday."""

body2 = """For the first time in the program's three-decade history, the H-1B lottery is not a lottery. The FY 2027 cap season that just ran was the debut of a wage-weighted selection system, and the early read on who it rewarded — and who it gutted — should reshape how every Indian professional thinks about the path to America.

## How the new math works

Under the old rule, every properly filed registration had the same shot: roughly a 30% chance, whether the job paid $80,000 or $280,000. That is gone. USCIS now assigns each candidate entries based on the Department of Labor's prevailing-wage level for the specific job and location:

- **Level IV** (most senior): 4 entries — an estimated 61% selection chance
- **Level III**: 3 entries — about 45%
- **Level II**: 2 entries — about 30%
- **Level I** (entry-level): 1 entry — about 15%

Everyone still lands in a single pool, and the statutory caps are unchanged: 65,000 plus 20,000 for U.S. advanced-degree holders. But the odds now bend, sharply, toward the highest-paid roles. A Level IV candidate is roughly four times likelier to be picked than a Level I one.

## The diaspora split this creates

This is where it gets personal for Indians, because the Indian H-1B population is not monolithic. It splits, roughly, into two camps — and the new rule treats them very differently.

The first camp is the FAANG-and-finance cohort: senior engineers, data scientists and product leads at large U.S. firms, frequently with U.S. master's degrees, slotted at Level III or IV. For them, the change is a windfall. Their selection odds have jumped from a coin-flip-that-usually-loses to a coin-flip-that-usually-wins. Skill and salary, not luck, now carry the day — exactly the meritocratic framing they have long argued for.

The second camp is the staffing-and-consulting cohort: workers placed through IT services and body-shop firms, historically registered in enormous volume at Level I and II wages. This is the group the rule was engineered to squeeze, and it worked. Their per-registration odds have collapsed toward 15-30%, and the firms that sponsor them — facing both worse odds and a separate $100,000 supplemental fee for consular cases — have slashed the number of registrations they file at all. Fewer entries, lower odds, higher costs: a triple hit.

## Recent Indian graduates are caught in the middle

The most anxious group may be Indian students finishing U.S. degrees. A new graduate's first job offer is frequently a Level I or II wage — not because the person is unskilled, but because prevailing-wage tables peg early-career roles low by design. Under random selection, that did not matter. Under wage weighting, it means a freshly minted master's holder from a strong U.S. program can be outbid, in pure lottery terms, by a more senior candidate with a higher salary.

The strategic response is already visible: negotiate harder on the offered wage level, target employers willing to file at Level II or above, and lean on the U.S. advanced-degree pool, which still carries its own 20,000 set-aside.

## A warning buried in the fine print

Selection is not approval. USCIS has signaled it will scrutinize whether the wage level claimed at registration actually matches the petition that follows. Inflating a wage level to grab more entries, then quietly filing at a lower one, is the kind of mismatch that invites a denial — or worse, a fraud referral. The wage you register at is now a commitment, not a guess.

## What's next

The rule survived its first season, but it is not bulletproof. It can still be challenged in court, and the broader political fight over the $100,000 fee — struck down by a federal judge in June and now on appeal — hangs over everything. For Indian professionals, though, the planning reality is already here: in the new H-1B, your salary is your lottery ticket. The higher the wage your employer is willing to certify, the better your odds of ever getting in the door."""

body3 = """The most expensive line item in American immigration is, for now, suspended in midair. The Trump administration's $100,000 fee on certain new H-1B petitions — the single largest cost ever attached to a U.S. work visa — was struck down by a federal judge in June. It is not dead. It is in appeal. And for Indian professionals, the gap between those two facts is where all the anxiety lives.

## What the court actually said

On June 8, the U.S. District Court for the District of Massachusetts vacated the fee. Judge Leo Sorokin, siding with a coalition of 20 states, ruled that President Trump's September 2025 proclamation had exceeded the fee-setting authority that Congress delegated to the executive. In plain terms: the court treated the $100,000 charge as an unauthorized tax dressed up as a regulatory fee, and said the White House cannot impose it by proclamation alone.

That ruling followed an earlier, opposite decision. In December 2025, a different federal court — in the District of Columbia — had *upheld* the fee, finding it fell within the president's broad power to restrict entry under 8 U.S.C. 1182(f). The U.S. Chamber of Commerce and the Association of American Universities appealed that one, and the D.C. Circuit agreed to fast-track it. So the program now carries two contradictory federal rulings and a pending appeal that the administration has confirmed it will pursue.

## Who the fee was built to hit

Understanding the stakes requires knowing the fee's narrow but brutal design. It applied generally to *new* H-1B petitions where the beneficiary is outside the United States and lacks a valid visa — that is, cases requiring consular notification. It did **not** apply to "change of status" petitions, the route by which an F-1 student already in the U.S. switches to H-1B without leaving.

That distinction draws a sharp line through the Indian diaspora. Students and recent graduates already on American soil — the F-1-to-OPT-to-H-1B pipeline — were largely spared, a clarification USCIS issued last October and one that quietly removed a six-figure obstacle for tens of thousands. The workers exposed were those abroad: new hires being brought in from India, and the staffing firms that move large numbers of consular H-1B cases. For them, $100,000 per petition was not a friction cost. It was a wall.

## Why limbo is its own punishment

A struck-down fee sounds like good news, and for now no one is being charged it. But uncertainty has a cost the diaspora knows intimately. Employers planning FY 2027 hires cannot price a role when the marginal cost of the visa might be $100,000 or might be zero, depending on an appellate ruling months away. Some have frozen overseas H-1B hiring entirely rather than gamble. Indian candidates waiting on offers from abroad are stuck in the same fog — a job that exists today might evaporate if the fee returns.

There is also the broader signal. Even policies later reversed by courts leave a mark, immigration experts note, because they tell prospective talent that the welcome mat is conditional. Indian green-card recipients have already fallen from 127,010 in 2022 to 66,800 in 2024. New U.S. citizens of Indian origin dropped nearly 25% over two years. The fee fight is one more data point telling skilled Indians to keep their options — and their Canadian and Gulf backup plans — warm.

## What to watch

Three things will decide how this lands. First, the D.C. Circuit appeal: a reversal of the Massachusetts ruling, or a clean appellate win for the administration, could revive the fee. Second, any move to re-impose the charge through formal rulemaking rather than proclamation, which would be far harder to strike down as procedurally improper. Third, the carve-out campaign — hospital associations and physician groups are lobbying Congress for a health-care exemption, betting the fee survives in some form and wanting their people out of its path.

For an Indian engineer weighing an offer that requires consular processing, the honest summary is this: the fee is not being collected right now, but do not treat its absence as permanent. The case is on a fast track, the administration is committed to the appeal, and the number that defined the most aggressive H-1B restriction in history is one ruling away from coming back."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "The Last Cheap Visa Slot in India Just Vanished. Now Every H-1B Line Is Months Long",
        "subheadline": "Appointment backlogs at U.S. consulates in India have hit 125-plus days, and Kolkata — the one fast lane Indians relied on — has collapsed from a 13-day wait to 126.",
        "slug": make_slug("us-consulate-india-visa-appointment-backlog-h1b-h4-kolkata-stamping"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "For two million H-1B and H-4 Indians, an expired visa stamp now means a routine trip home can strand them abroad for a third of a year, away from jobs employers can't legally hold open.",
        "tags": ["h1b", "h4", "visa-stamping", "consulate", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Fragomen — Update on Visa Appointment Backlogs at U.S. Consulates in India", "url": "https://www.fragomen.com/insights/lengthy-visa-appointment-backlogs-at-u-s-consulates-in-india.html"},
            {"name": "Reddy Neumann Brown PC — Consulates Pushing H-1B & H-4 Interviews to Mid-2026", "url": "https://www.rnlawgroup.com/stop-holiday-travel-for-stamping-consulates-are-pushing-h-1b-h-4-interviews-to-mid-2026/"},
            {"name": "Tafapolsky & Smith LLP — Consulates Rescheduling H-1B and H-4 Appointments", "url": "https://www.tandslaw.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "An open passport displaying visa and travel stamps",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body1,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The H-1B Lottery Is No Longer a Lottery. For Indians, Your Salary Is Now Your Ticket",
        "subheadline": "The FY 2027 cap season was the first run of wage-weighted selection — handing senior, higher-paid Indians up to a 61% chance while gutting the odds for entry-level and staffing-firm workers.",
        "slug": make_slug("h1b-wage-weighted-selection-fy2027-lottery-indians-wage-levels"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The new wage-weighted draw splits the Indian H-1B pool in two: senior tech and finance professionals win big, while recent graduates and staffing-firm hires at Level I-II wages see their odds collapse.",
        "tags": ["h1b", "uscis", "wage-selection", "lottery", "india", "immigration"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — The $100,000 question: Navigating the new H-1B lottery system", "url": "https://www.reuters.com/legal/legalindustry/100000-question-navigating-new-h-1b-lottery-system-2026-03-24/"},
            {"name": "SHRM — USCIS Replaces Random H-1B Lottery with Wage-Weighted Selection", "url": "https://www.shrm.org/topics-tools/news/talent-acquisition/uscis-replaces-random-h-1b-lottery-wage-weighted-selection"},
            {"name": "Greenberg Traurig (Lexology) — USCIS Finalizes Wage Weighted H-1B Cap Selection Rule", "url": "https://www.lexology.com/library/detail.aspx?g=uscis-finalizes-wage-weighted-h-1b-cap-selection-rule"}
        ]),
        "score_total": 80,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/8441786/pexels-photo-8441786.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A professional reviewing an application form at a desk",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body2,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Judge Killed the $100,000 H-1B Fee. The Government Is Bringing It Back to Life",
        "subheadline": "The largest fee ever attached to a U.S. work visa was struck down in June — but with the administration appealing and a rival ruling upholding it, Indian professionals are stuck planning around a number that may return.",
        "slug": make_slug("h1b-100000-fee-struck-down-appeal-dhs-indians-limbo-sorokin"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The $100,000 fee spared F-1 students switching to H-1B inside the U.S. but walled out new hires from India — and its uncertain legal status is freezing overseas hiring that Indian candidates depend on.",
        "tags": ["h1b", "visa-fee", "court-ruling", "dhs", "india", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Wisconsin Hospital Association — U.S. District Court Vacates $100,000 H-1B Visa Filing Fee", "url": "https://www.wha.org/"},
            {"name": "Reuters — US appeals court fast tracks $100,000 H-1B visa fee dispute", "url": "https://www.reuters.com/legal/government/us-appeals-court-fast-tracks-100000-h-1b-visa-fee-dispute-2026-01-06/"},
            {"name": "Outlook Business — US Plans 75% Citizenship Fee Hike; Boston court struck down H-1B fee", "url": "https://www.outlookbusiness.com/"}
        ]),
        "score_total": 82,
        "status": "review",
        "image_url": "https://images.pexels.com/photos/36984937/pexels-photo-36984937.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The facade of a U.S. courthouse with neoclassical columns",
        "image_attribution": "Pexels",
        "is_editorial": False,
        "body": body3,
    },
]

# word-count sanity
for art in articles:
    wc = len(art["body"].split())
    print(f"   {art['slug']} -> {wc} words")

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
