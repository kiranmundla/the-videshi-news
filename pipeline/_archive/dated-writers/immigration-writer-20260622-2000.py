#!/usr/bin/env python3
"""Insert 2 fresh immigration articles for The Videshi (2026-06-22 2000).
Topics (verified not covered in last 3 days):
  1. Indian student enrollment collapse in the US (6.9% MEA/SEVIS drop, GMAC 45%
     new-enrollment fall, F-1->H-1B pipeline at risk)
  2. FY2027 H-1B cap season closes June 30 — first wage-weighted lottery, $100K
     fee impact on staffing firms, who won and lost under the new system
All status=review, is_editorial=False, category/vertical=immigration.
"""
import os, json, subprocess

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ["SUPABASE_KEY"]

ARTICLES = [
# ------------------------------------------------------------------ 1
{
  "slug": "indian-student-enrollment-collapse-us-universities-sevis-gmac-f1-h1b-pipeline-20260622",
  "category": "immigration",
  "vertical": "immigration",
  "urgency": "medium",
  "headline": "The Pipeline Is Drying Up: Why Indian Students Are Quitting America",
  "subheadline": "India's government has confirmed the sharpest fall in Indian enrolment in US universities in over a decade \u2014 down 6.9% in a single year. With new-student numbers dropping far faster, the corridor that feeds the H-1B workforce is narrowing at both ends.",
  "diaspora_angle": "Roughly 71% of H-1B holders are Indian, and the overwhelming majority arrive first as F-1 students; a collapse in student enrolment today is a contraction of the diaspora's primary on-ramp to America tomorrow.",
  "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  "image_caption": "Students cross a university campus in the United States. India remains the largest source of international students, but most US institutions are now reporting declines from India.",
  "image_attribution": "George Pak / Pexels",
  "tags": ["indian-students", "f1-visa", "enrollment", "study-abroad", "h1b-pipeline", "immigration"],
  "sources": [
    {"name": "The Hindu BusinessLine \u2014 Indian student enrolment in US falls nearly 7% amid stricter visa rules", "url": "https://www.thehindubusinessline.com/news/education/"},
    {"name": "Collegedunia \u2014 Indian Students in US Fall 6.9% to 3.52 Lakh, Sharpest Drop in a Decade (Parliament Data)", "url": "https://collegedunia.com/news"},
    {"name": "Times of India / GMAC \u2014 45% drop in Indians at US universities over visa concerns", "url": "https://timesofindia.indiatimes.com/education"},
    {"name": "ICEF Monitor \u2014 New survey data says demand for MBA study abroad is shifting", "url": "https://monitor.icef.com/"}
  ],
  "body": """When India's Ministry of External Affairs answered a question in the Rajya Sabha on April 2nd, the numbers it produced were drier than the anxiety they confirmed. The total number of Indian students in the United States, the ministry reported, had fallen from 378,787 in February 2025 to 352,644 a year later \u2014 a decline of about 6.9 percent. Drawn from the US Department of Homeland Security's own student-tracking system, it was the sharpest single-year drop in more than a decade.

The headline figure understates the turn. A 6.9 percent fall in the total student body is what you see after a year in which the people already enrolled mostly stay put. The leading edge \u2014 new arrivals \u2014 has fallen off a cliff. Indian student arrivals dropped 44 percent between August 2024 and August 2025, the largest single-country decline any tracker recorded, and a GMAC white paper logged a 45 percent fall in new Indian enrolments at US universities over the same window. A snapshot of more than 800 institutions found 57 percent reporting fewer new international students for the 2025\u201326 year, with most citing declines from India specifically.

## A corridor narrowing at both ends

For the Indian diaspora, this is not an education story that happens to involve visas. It is an immigration story that happens to begin in a classroom.

The path is well worn: a student arrives on an F-1 visa, completes a degree, works on Optional Practical Training, and \u2014 if the lottery is kind \u2014 converts to an H-1B and, eventually, joins the decades-long queue for a green card. Indians make up roughly 71 percent of all H-1B holders, and the overwhelming majority of them entered the country as students first. The F-1 visa is the front door to the entire structure. When fewer Indians walk through it, the contraction shows up years later in every downstream category the community depends on.

That is what makes the current numbers more than a bad season for university admissions offices. The students who are not arriving in 2026 are the H-1B applicants who will not exist in 2029, and the green card filers who will not exist in the 2030s. A pipeline is being throttled at its source.

## Why they are staying away

The reasons are not mysterious, and they compound. Visa processing for Indian applicants has been slow, scrutiny has intensified, and interview availability in India has been erratic \u2014 a May-to-June suspension of appointments paired with new social-media vetting requirements produced what some reports estimated as an 80 to 90 percent collapse in June issuances. F-1 visas issued to Indians had already fallen 33 percent in one recent fiscal year before these latest disruptions.

Then there is the math families do at the kitchen table. American tuition is high, the rupee is weak, and the post-study payoff \u2014 once the implicit promise of the whole arrangement \u2014 now looks fragile against an H-1B program reshaped by a $100,000 fee and a hiring market that artificial intelligence is cooling. When the destination's own signals say foreign workers are less welcome, the calculus of borrowing heavily to study there changes.

## The competition has noticed

Students are not abandoning higher education abroad; they are rerouting it. GMAC found that non-US candidates' preference for studying in America fell to 42 percent in 2025, from 57 percent in 2019, while interest in Western Europe held steady at 63 percent and demand for programmes across Asia and Eastern Europe rose. Two-thirds of business-school programmes in the Americas reported enrolment declines; a majority in the Asia-Pacific reported increases. Even India's own graduate-management programmes saw a 25 percent rise in international applications.

The cost of the drift is concrete. One projection cited by analysts put a potential loss of 150,000 international students at roughly $7 billion to the US economy and 60,000 jobs. India remains the single largest source of foreign students in America \u2014 but for the first time since 2019, the gap with second-ranked China has narrowed, a reversal that would have seemed implausible a few years ago.

## What the diaspora stands to lose

For families already settled in the United States, the enrolment collapse can feel like someone else's problem \u2014 until it is reframed. The diaspora's strength in America was built on a self-renewing pipeline: each cohort of students became workers, who sponsored the next generation and seeded the next. That renewal is now in question.

A community does not shrink in a single year. But the inputs that sustain it are being cut, quietly, in admissions decisions made an ocean away. The students choosing Munich or Singapore over Boston in 2026 are voting on whether the American chapter of the Indian diaspora keeps growing \u2014 and, for now, an increasing number are voting no."""
},
# ------------------------------------------------------------------ 2
{
  "slug": "fy2027-h1b-cap-season-closes-june-30-wage-weighted-lottery-100k-fee-staffing-firms-20260622",
  "category": "immigration",
  "vertical": "immigration",
  "urgency": "high",
  "headline": "The First Wage-Weighted H-1B Season Ends Monday. The Rules Changed Everything.",
  "subheadline": "The window to file FY2027 H-1B petitions closes June 30 \u2014 the close of the first cap season run on a salary-weighted lottery instead of pure chance. Paired with a $100,000 fee that gutted staffing-firm registrations, it has quietly rewritten who gets to come.",
  "diaspora_angle": "Indians win the H-1B lottery more than any other nationality, so a system that now rewards higher salaries and punishes the staffing-firm model reshapes the odds for hundreds of thousands of Indian professionals more than for anyone else.",
  "image_url": "https://images.pexels.com/photos/6424583/pexels-photo-6424583.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=2",
  "image_caption": "Code on a developer's screen. The FY2027 H-1B cap season was the first run under a wage-weighted selection system that favours higher-paid specialty workers.",
  "image_attribution": "Nemuel Sereti / Pexels",
  "tags": ["h1b", "fy2027", "wage-weighted-lottery", "100k-fee", "uscis", "immigration"],
  "sources": [
    {"name": "USCIS \u2014 FY 2027 H-1B Cap Initial Registration Period Opens on March 4", "url": "https://www.uscis.gov/newsroom"},
    {"name": "Bloomberg Tax \u2014 Employers Hit H-1B Worker Cap for Fiscal Year 2027, USCIS Says", "url": "https://news.bloombergtax.com/"},
    {"name": "HSF Kramer (via Lexology) \u2014 US DHS Implements Weighted Selection Process for FY 2027 H-1B Cap Registrations", "url": "https://www.hsfkramer.com/insights"},
    {"name": "Federal Register \u2014 Weighted Selection Process for Registrants and Petitioners Seeking to File Cap-Subject H-1B Petitions", "url": "https://www.federalregister.gov/documents/2025/12/29/2025-23853/weighted-selection-process-for-registrants-and-petitioners-seeking-to-file-cap-subject-h-1b"}
  ],
  "body": """On Monday, June 30th, the filing window for fiscal-year 2027 H-1B petitions closes. For employers who won a slot in this spring's lottery, it is the last day to get a petition in the door. For everyone watching the program, it marks the end of the most consequential cap season in years \u2014 the first run entirely under rules designed to change who an H-1B goes to.

For two decades the H-1B lottery was an act of pure chance. Registrations exceeded the 85,000 annual cap, so a computer drew names at random; a junior coder at a body shop and a senior engineer at a marquee firm had identical odds. This year, that ended. Under a Department of Homeland Security final rule, selection is now weighted by salary. A beneficiary offered a wage in the Department of Labor's top tier, Level IV, receives four entries in the pool; Level III gets three, Level II two, and Level I a single entry. The same number of visas, allocated by a very different logic.

## Two policies, one squeeze

The wage rule did not arrive alone. It landed alongside a presidential proclamation imposing a $100,000 fee on certain H-1B petitions \u2014 broadly, those for workers outside the United States who require consular processing. Together the two measures pull in the same direction, and they fall hardest on a specific business model.

For years, IT staffing firms \u2014 many of them Indian-owned \u2014 flooded the lottery with tens of thousands of registrations for entry-level consultants, playing the volume game that random selection rewarded. Both new rules dismantle that strategy at once. The wage weighting gives their typically lower-paid Level I and II candidates the fewest entries, while the $100,000 fee makes filing for an overseas hire economically ruinous. Immigration analysts expected staffing companies to slash their registrations sharply as a direct result \u2014 and, counterintuitively, that withdrawal raises the overall selection rate for everyone who remains in the pool.

## What the early signals show

The mechanics played out roughly on schedule. USCIS opened registration from March 4th to 19th, ran its first weighted selection by the end of March, and opened petition filing on April 1st. In late March the agency confirmed it had received enough registrations to hit the statutory cap \u2014 the program is not collapsing for lack of demand \u2014 and Bloomberg reported that this March drawing was, in its words, the first held under regulations weighting odds toward workers who are more senior and more highly paid.

What changed beneath that headline is the composition of the winners. The system is built to advantage exactly the profile that established technology employers field: experienced specialists commanding higher salaries, filing change-of-status petitions for people already in the country on F-1 or other visas \u2014 a category the $100,000 fee generally does not touch. The losers are the high-volume, lower-wage registrations that defined the staffing-firm era, and the candidates abroad for whom the six-figure fee is simply prohibitive.

## Why this lands on Indians hardest

No nationality is more exposed to these changes than Indians, who win the H-1B lottery more often than every other country combined. A shift in the rules of selection is, functionally, a shift in the rules for the Indian diaspora's most important work visa.

The effect cuts two ways. An Indian professional with a US master's degree and a strong salary offer from a major employer may find the new system genuinely friendlier: fewer staffing-firm registrations crowding the pool means better odds, and a change-of-status filing sidesteps the fee entirely. But the Indian engineer earning an entry-level wage, or the candidate still in India hoping a consultancy will sponsor a first US job, faces a program that has been deliberately tilted away from them. The ladder's bottom rungs are being sawed off even as the upper rungs hold.

## A structural reset, not a tweak

It is tempting to read each measure as one more line in a long list of H-1B adjustments. Taken together, they are something larger: a reengineering of the visa's purpose from a broad talent lottery into a narrow channel for high-wage, high-skill hires, with the staffing-firm pipeline that built much of Indian-American tech employment squeezed out by design.

When the window shuts on Monday, the FY2027 numbers will begin to settle into the record \u2014 how far staffing registrations actually fell, how much the selection rate rose for those who stayed, and which wage levels ultimately filled the cap. The full picture will take months to resolve. But the direction is already set, and for Indian workers weighing whether America still offers a viable path, the message of this first wage-weighted season is unambiguous: the door is not closing, but it is being rebuilt to a narrower frame."""
}
]


def insert(article):
    payload = dict(article)
    payload["sources"] = json.dumps(article["sources"])
    payload["is_editorial"] = False
    payload["is_featured"] = False
    payload["status"] = "review"
    body = json.dumps([payload])
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {KEY}",
        "-H", f"Authorization: Bearer {KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", body,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        res = json.loads(out.stdout)
    except Exception:
        return False, out.stdout[:500]
    if isinstance(res, list) and res and res[0].get("id"):
        wc = len(article["body"].split())
        return True, f"{res[0]['id']}  (~{wc} words)"
    return False, str(res)[:500]


if __name__ == "__main__":
    print("Inserting", len(ARTICLES), "immigration articles (status=review)\n")
    ok = 0
    for a in ARTICLES:
        success, msg = insert(a)
        flag = "OK " if success else "FAIL"
        if success: ok += 1
        print(f"[{flag}] {a['slug']}\n        {msg}\n")
    print(f"Done: {ok}/{len(ARTICLES)} inserted.")
