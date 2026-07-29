/* ------------------------------------------------------------------ */
/* Kids Guide Content                                                 */
/* Static guide data — can move to Supabase later                     */
/* ------------------------------------------------------------------ */

export interface GuideSection {
  heading: string;
  content: string; // markdown
}

export interface KidsGuide {
  topic: string;       // matches ALL_GUIDES key in KidsPage
  slug: string;        // URL slug
  title: string;
  icon: string;
  summary: string;
  sections: GuideSection[];
}

const GUIDES: KidsGuide[] = [
  {
    topic: "math",
    slug: "math-competitions",
    title: "Math Competitions — The Complete Path",
    icon: "🔢",
    summary: "From Math Kangaroo to AMC/AIME, here's how to get your child started on the competitive math track and what to expect at each level.",
    sections: [
      {
        heading: "Why Math Competitions?",
        content: `Let's get the obvious out of the way: yes, math competitions look good on college applications. But that's actually the least interesting reason to do them.

What math competitions really teach is **how to think about problems you've never seen before**. School math is mostly about applying formulas you've been taught. Competition math is about figuring out *which* approach might work — and being comfortable when your first idea doesn't. That skill transfers to everything: science, engineering, computer science, even business.

The numbers tell the story of how popular this has become. In 2026, over **80,000 students** took the AMC 8 (the main middle school competition). **Math Kangaroo** drew **60,504 participants** across all grade levels, up from 53,562 the year before. **MOEMS** (Math Olympiad for Elementary and Middle Schools) reaches **120,000+ students** across all 50 states and 39 countries. These aren't niche activities anymore.

For many students, the real benefit is finding their people. In a regular classroom, the kid who loves math puzzles might feel out of place. At a math competition or math circle, they're surrounded by kids who think the same way. That sense of belonging matters more than any trophy.`
      },
      {
        heading: "The Competition Landscape",
        content: `Here's what's available at each level. Don't try to do everything — pick what fits your child's age and interest.

### Elementary School (Grades 2–6)

**Math Kangaroo** — The gentlest on-ramp. A 75-minute multiple-choice test with 24 questions for grades K–4 or 30 questions for grades 5–12. Problems are creative and visual — less about calculation, more about logical thinking. Every participant gets a small gift, which matters when you're 7. Registration is **$18–20 per student** (regular) or $35 late. Held every March at schools and community centers. Great first competition.

**MOEMS (Math Olympiad for Elementary and Middle Schools)** — A season-long program, not a single test. Five contests spread across November to March, each with 5 problems in 30 minutes. Division E covers grades 4–6. Teams of up to 35 students register together for **$175–300 per team** (that's roughly $5–9 per student). About half of all participants earn at least one award, so the recognition rate is generous. Your school or a parent can organize a team.

**Noetic Learning Math Contest** — Twice a year (fall and spring), 20 questions in 45 minutes for grades 2–8. Registration is **$99 per team**. Good for younger students who aren't ready for AMC-level difficulty.

### Middle School (Grades 6–8)

**AMC 8** — The big one for middle schoolers. Run by the Mathematical Association of America (MAA). 25 multiple-choice questions in 40 minutes, held every January. In 2026, about **81,000 students** participated. The cost is minimal — schools pay a bundle fee of **$25 for 10 student licenses** (about $2.50 per student). Some external test centers charge $30–80. The top 1% earn Distinguished Honor Roll (score of 24+ in 2026), and the top 5% earn Honor Roll (21+ in 2026). This is many students' first taste of "real" competition math.

**MATHCOUNTS** — The premier middle school math competition, with a tournament-style structure that builds excitement: School → Chapter → State → National. It combines individual rounds (Sprint: 30 questions in 40 minutes; Target: 4 pairs of problems) with a Team Round and a thrilling Countdown Round. Registration is **$40–50 per student** through schools (max 14 students), or **$70–80** for non-school competitors. The national competition, held every May, is genuinely prestigious.

**MOEMS Division M** — Same format as Division E, but for grades 6–8 with harder problems.

### High School (Grades 9–12)

**AMC 10 / AMC 12** — The gateway to the serious competition pipeline. 25 questions, 75 minutes, multiple choice, held every November (two sittings: A and B). AMC 10 is for grades 10 and below; AMC 12 is for grades 12 and below. The site registration fee for schools is **$55–115** depending on timing, with student bundles at **$30 for 10 licenses** ($3 per student). External test centers typically charge $30–80 per student.

**AIME (American Invitational Mathematics Examination)** — By invitation only. Roughly the top 2.5%–5% of AMC 10/12 scorers qualify (about 6,000–7,000 students annually since 2020). 15 questions, 3 hours, integer answers (0–999). This is where the difficulty jumps significantly.

**USA(J)MO** — The top tier. Based on combined AMC + AIME scores, about 250–500 students are invited to the USA Mathematical Olympiad (USAMO) or USA Junior Mathematical Olympiad (USAJMO). These are proof-based exams — a completely different skill from multiple choice. The very top performers (around 50–60) are invited to the Mathematical Olympiad Program (MOP), which selects the 6-member team for the International Mathematical Olympiad (IMO).`
      },
      {
        heading: "The Typical Path — What's Realistic",
        content: `Here's a rough timeline that many families follow. Adjust based on your child — some start earlier, some later, and both are fine.

**Grades 2–4: Exploration.** Try Math Kangaroo or Noetic. The goal is to see if your child enjoys puzzles and non-routine problems. No prep courses needed — just hand them some interesting problems and see if their eyes light up.

**Grades 4–6: Foundation.** If they're interested, MOEMS is a great team experience. Start thinking about AMC 8 preparation. This is when many families introduce Art of Problem Solving (AoPS) books or Beast Academy. The key is building problem-solving habits, not cramming.

**Grades 6–8: Engagement.** AMC 8 and MATHCOUNTS become the focus. A student who scores 18+ on AMC 8 is doing well. A score of 21+ (Honor Roll, top 5%) is excellent. MATHCOUNTS adds the competitive team element that many kids love.

**Grades 9–10: The Fork.** AMC 10 is the next step. Qualifying for AIME (roughly a score of 100–105+ out of 150) is a meaningful achievement that relatively few students reach. This is where you see the split between students who enjoy competition math as an enrichment activity and those pursuing it at the highest level.

**Grades 11–12: For the Dedicated.** AMC 12, AIME, and potentially USAMO. At this level, most successful students have been doing competition math for years and are putting in serious hours.

**The honest truth:** Getting to AIME is achievable for a motivated, well-prepared student. Getting to USAMO requires exceptional talent *and* years of dedicated practice. Getting to IMO is a "one in a generation" kind of thing. Most families should think of AMC Honor Roll and MATHCOUNTS as great outcomes — because they are.`
      },
      {
        heading: "How to Get Started — Practical Steps",
        content: `### Free Resources (start here)

- **Past AMC/MATHCOUNTS problems** — Available free on the Art of Problem Solving wiki. This is the single best preparation: work through real past problems.
- **Alcumus** (by AoPS) — A free adaptive online problem bank that adjusts to your child's level. Excellent for daily practice.
- **MATHCOUNTS Problem of the Week** — Free weekly problems on mathcounts.org. Great for building a practice habit.
- **Math Kangaroo past problems** — Available on mathkangaroo.org with video solutions.

### Books

- **Beast Academy** (AoPS, grades 2–5) — Comic-book-style math curriculum that makes problem-solving engaging. Guides are ~$18, practice books ~$13.
- **Art of Problem Solving textbooks** (middle/high school) — The gold standard. Prealgebra, Introduction to Algebra, Introduction to Counting & Probability, Introduction to Number Theory, Introduction to Geometry. Books run **$50–60 each** with solution manuals.
- **Competition Math for Middle School** by Jason Batterson — A popular, more affordable alternative (~$30).

### Online Courses

- **AoPS Online** — Structured courses with live (text-based) instruction. MATHCOUNTS/AMC 8 Basics runs about **$245** for 12 sessions. Introduction-level courses (Algebra, Geometry, etc.) are **$265–500** for 12–36 sessions. The teaching quality is exceptional, but the format (text-based chat, not video) takes getting used to.
- **Think Academy** — Video-based instruction, popular in the South Asian and East Asian community. AMC 8 prep courses are available year-round.
- **Ivy League Education Center** — Intensive weekend AMC 8/MATHCOUNTS prep courses, typically **$530–875** for 15–24 hour sessions.

### In-Person Options

- **Math circles** — Free or low-cost weekly gatherings run by university math departments or parent volunteers. Search "math circle" + your city. The Bay Area has several excellent ones.
- **Russian School of Mathematics (RSM)** — Rigorous after-school math program with locations across the US. Tuition typically runs **$200–300+ per month** depending on level and location. Strong track record in competitions.
- **Kumon / Mathnasium** — These focus more on grade-level mastery than competition prep, but can help build foundational speed and accuracy. Kumon runs about $150–200/month; Mathnasium is similar.

### School Registration

For AMC and MATHCOUNTS, your child's school needs a "Competition Manager" (usually a math teacher) to register. If your school doesn't participate, you have options:
- Ask a math teacher to register — most of the work is handled by MAA/MATHCOUNTS
- Find an external test center (search on maa.org)
- For MATHCOUNTS, register as a Non-School Competitor ($70–80)
- For Math Kangaroo, any parent can start a center at their school (free for the school)`
      },
      {
        heading: "What It Costs — The Real Numbers",
        content: `Math competitions are one of the more affordable extracurriculars. Here's what families actually spend:

### Competition Fees Only (the minimum)
| Competition | Cost per Student | When |
|---|---|---|
| Math Kangaroo | $18–20 | March |
| AMC 8 (through school) | $2.50–5 | January |
| AMC 8 (test center) | $30–80 | January |
| MOEMS (team of 35) | ~$5–9/student | Nov–Mar |
| MATHCOUNTS (school) | $40–50 | Year-round |
| MATHCOUNTS (non-school) | $70–80 | Year-round |
| AMC 10/12 (through school) | $3–5 | November |
| AMC 10/12 (test center) | $30–80 | November |
| Noetic Learning | ~$5–10/student | Fall & Spring |

### With Self-Study (moderate budget)
Competition fees + AoPS books: **$100–300/year.** This is the path many successful students take. The books are outstanding, and combined with free online resources, it's enough to do very well.

### With Structured Prep (higher budget)
Add online courses or in-person tutoring: **$1,000–5,000+/year.** An AoPS course or two plus competition fees. Or RSM tuition at $200–300/month.

### The Intensive Track
Multiple prep courses, private tutoring, summer camps: **$5,000–15,000+/year.** This level of spending is common among families targeting AIME/USAMO, but it's not necessary for most students to have a great competition experience.

**Bottom line:** A student can participate meaningfully in math competitions for under $100/year. The expensive part is optional prep, not the competitions themselves.`
      },
      {
        heading: "The South Asian Community Connection",
        content: `South Asian families are significantly represented in US math competitions, and that's worth acknowledging openly.

At the 2026 MATHCOUNTS National Competition, at Scripps National Spelling Bee, and at top AMC scorers lists, Indian-American students consistently appear in large numbers. This reflects a genuine cultural emphasis on academic excellence and a strong community infrastructure — from tutoring networks to parent study groups to WhatsApp channels sharing competition tips.

This has real advantages for your family:
- **Community knowledge** — Other parents in your network have likely navigated this path and can share advice on local resources, which test centers work best, and how to pace preparation.
- **Study groups** — It's easier to find practice partners and form MATHCOUNTS teams when families around you are also interested.
- **Local programs** — Many Bay Area math enrichment centers (Think Academy, RSM, Alpha Star Academy) serve communities with high competition participation and understand what families are looking for.

But it also comes with pressure. Not every kid who's good at math enjoys competition math. The problem-solving style is very different from school math, and some brilliant math students simply don't enjoy timed tests. That's completely fine. Competition math is one path, not the only path, to developing strong mathematical thinking.`
      },
      {
        heading: "The Honest Take — Is This Right for Your Child?",
        content: `### Signs your child might thrive
- They enjoy puzzles, brain teasers, or logic games on their own
- They get bored with repetitive math homework but light up with a challenging problem
- They want to understand *why* something works, not just *how* to get the answer
- They handle frustration reasonably well — competition problems are supposed to be hard
- They have some competitive spirit (or at least enjoy the social aspect of team competitions)

### Signs to pause and reconsider
- They're doing it primarily because you want them to, not because they're interested
- They're already stressed about school and adding competition pressure would be too much
- They associate math with anxiety — competition won't fix that, and might make it worse
- They're comparing themselves unfavorably to peers and losing confidence

### Watch for burnout
This is the biggest risk, especially in communities where competition math is the norm. A child who loved Math Kangaroo at age 8 might burn out by middle school if the intensity ramps up too fast. Signs to watch:
- Resistance to practice that used to be fun
- Anxiety before competitions that wasn't there before
- Defining their self-worth by scores and rankings
- Losing interest in math entirely

If you see these signs, pull back. Take a break. Let them come back to it when (or if) they're ready.

### The best approach
Start casual. Try Math Kangaroo or a local math circle. See if the spark is there. If it is, add structure gradually — an AoPS book, then maybe a course. Let your child's enthusiasm drive the pace, not a parent's timeline for AIME qualification.

The students who go furthest in math competitions are almost always the ones who genuinely enjoy the problems. You can't manufacture that enjoyment, but you can create the conditions for it to develop.`
      },
      {
        heading: "Key Dates to Know (2026–2027 School Year)",
        content: `| Competition | Registration Deadline | Competition Date |
|---|---|---|
| MOEMS | Early bird: Jul 31 / Standard: Oct 15 | Monthly, Nov 2026 – Mar 2027 |
| AMC 10A / 12A | Early bird: Sep 30 / Regular: Oct 15 | November 5, 2026 |
| AMC 10B / 12B | Same as above | November 13, 2026 |
| MATHCOUNTS (School) | Dec 15, 2026 | School: Aug–Jan / Chapter: Feb / State: Mar / National: May |
| Math Kangaroo | Regular: Dec 31 / Late: Feb 1 | March 18, 2027 |
| AMC 8 | Early bird: Oct 28 / Regular: Jan 5 | January 21–27, 2027 |

**Pro tip:** Mark the registration deadlines, not just the competition dates. Many parents miss deadlines and end up paying late fees or missing the competition entirely. September is when you should be planning the year.

*Dates shown are for the 2026–2027 cycle. Check official websites for the most current information: [maa.org](https://maa.org) for AMC, [mathcounts.org](https://mathcounts.org) for MATHCOUNTS, [mathkangaroo.org](https://mathkangaroo.org) for Math Kangaroo, [moems.org](https://moems.org) for MOEMS.*`
      }
    ]
  },
  {
    topic: "spelling_debate",
    slug: "spelling-bee",
    title: "Spelling Bee — From School to Nationals",
    icon: "🐝",
    summary: "Everything parents need to know about spelling bees: South Asian Spelling Bee, Scripps, NSF — the preparation path, costs, and what makes it rewarding.",
    sections: [
      {
        heading: "Why Spelling Bees?",
        content: `Spelling bees are one of those rare activities where a child stands alone on a stage, listens carefully, asks the right questions, and performs under pressure — all skills that matter far beyond spelling.

What kids actually gain:

- **Vocabulary and language depth.** Serious spellers don't just memorize letter sequences. They learn Greek and Latin roots, language patterns, and etymology. A child who knows that "pneumo-" means lung and "-itis" means inflammation understands medical terminology, not just how to spell "pneumonitis." That kind of structural language knowledge pays dividends in reading comprehension, standardized tests, and writing — for years.
- **Discipline and study habits.** Preparing for a spelling bee teaches kids how to build a study routine, break a large task into smaller pieces, and stick with something over months. These are the same skills they'll need for any academic pursuit.
- **Poise and public performance.** Standing at a microphone in front of an audience, staying calm, asking for a definition or language of origin — that's public speaking practice in disguise. Many parents report that spelling bees gave their shy child a new kind of confidence.

The numbers reflect how popular this has become. The **Scripps National Spelling Bee** — the big one — drew **247 spellers** to its 2026 national finals in Washington, D.C., representing all 50 states and five countries. But those 247 are the tip of the iceberg: an estimated **11 million students** participate in school-level spelling bees across the country each year through the Scripps program, with schools paying $199 each to enroll. Add in the South Asian Spelling Bee, North South Foundation bees, and dozens of regional and community competitions, and spelling bees are one of the most accessible academic competitions in America.`
      },
      {
        heading: "The Competition Landscape",
        content: `There are three major spelling bee pathways worth knowing about. Each has a different format, audience, and feel.

### Scripps National Spelling Bee — The Big One

This is the competition you see on ESPN. Founded in 1925, it's the oldest and most prestigious spelling bee in the country.

**How it works:** Your child's school enrolls in the Scripps program ($199 per school, or $135 for homeschool families). The school runs a classroom bee, then a school bee. The school champion advances to a regional bee (typically February–March), organized by a local sponsor (often a newspaper or media company). Regional champions earn an **all-expenses-paid trip** to Bee Week in Washington, D.C., held every May.

**Eligibility:** Students must not have passed beyond 8th grade or turned 15 before August 31 of that school year. That's it — no minimum age or grade.

**Format (2026):** Preliminary rounds include spelling and vocabulary from the *Words of the Champions* study guide (4,000 words). Later rounds draw from the full Merriam-Webster Unabridged Dictionary — essentially unlimited. The 2026 finals featured a 90-second "spell-off" tiebreaker where finalists raced to spell as many words as possible.

**What the winner gets:** $52,500 cash, the Scripps Cup trophy, reference works from Merriam-Webster and Britannica, and $1,000 in Delta Air Lines credits.

**Cost to families:** Essentially free for students. The school pays $199 to enroll. Regional bees are typically free for qualified spellers. Scripps covers travel, lodging, and event access for national qualifiers and one guardian.

### South Asian Spelling Bee (SASB)

Run by the South Asian Education Foundation (SAEF), this is the community's own competition and it matters a lot to many families.

**How it works:** Virtual regionals are held across 5 city-named rounds (you can join any regardless of location — cities are just scheduling labels). Top spellers from each regional advance to the national finals. There's also the **SAS-Bee** wildcard pathway: up to 100 students apply ($75 application fee), 20 are shortlisted, and the first 12 to confirm get a seat at finals ($250 finals fee).

**Eligibility:** Under 15 years old, with at least one parent or grandparent of South Asian descent (India, Pakistan, Bangladesh, Sri Lanka, Nepal, Bhutan, Afghanistan, or Maldives).

**Registration:** $50 per speller for regionals. Includes a practice word list.

**Why it matters:** The SASB is broadcast on Sony Entertainment Television (SET) Asia to over 120 countries. For many Indian-American kids, this is their first on-stage competitive spelling experience in a familiar community setting. The atmosphere is supportive, and it's a great stepping stone to Scripps.

### North South Foundation (NSF) Spelling Bee

NSF runs academic contests across 75+ chapters in the US, with all registration fees going toward scholarships for underprivileged students in India. The spelling bee is one of several subjects offered (they also run math, science, geography, vocabulary, and public speaking contests).

**How it works:** Regional contests are held at local chapters each spring. Top-ranked students are invited to the National Finals in summer, where they compete for scholarships and trophies.

**Levels:** Junior Spelling Bee (grades 1–3) and Senior Spelling Bee (grades 4–8). NSF provides 1,000 practice words after registration.

**Cost:** $40 per contest for regionals, $60 for national finals.

**Why it's special:** NSF bees are deeply embedded in the Indian-American community. They're run entirely by volunteers, and participating means your child is also contributing to education funding in India. Many families do NSF alongside Scripps — the two don't conflict.

### Other Spelling Bees

- **98thPercentile National Spelling Bee** — Free, online, for grades 3–8. A low-pressure way to try competitive spelling.
- **School and district bees** — Many school districts run their own independent spelling programs outside of Scripps.
- **Community and temple bees** — Hindu temples, cultural organizations, and community groups often host informal spelling bees. Great for very young beginners.`
      },
      {
        heading: "The Typical Path — What's Realistic",
        content: `**Grades 1–3: Discovery.** Most kids encounter spelling bees through their school's classroom bee. At this age, the goal is simply exposure. If your child enjoys word games, puzzles, or reading, try the NSF Junior Spelling Bee or a community bee. Don't start formal prep — just encourage reading and curiosity about words.

**Grades 3–5: Building the Foundation.** This is when many serious spellers begin. If your school is enrolled in Scripps, your child can compete in the school bee. Start with the *Words of the Champions* list — it's free and it's the official source for early rounds. Many families also register for NSF and SASB around this age. This is when kids learn study techniques: flashcards, root words, language-of-origin patterns.

**Grades 5–7: The Competitive Window.** This is peak spelling bee age. Students have enough vocabulary foundation to tackle harder words, and they still have multiple years of eligibility left. A child who makes it to their regional Scripps bee in 5th or 6th grade has two or three more chances to advance. Most national-level spellers hit their stride in this range.

**Grade 8: Last Shot.** Eighth grade is the final year of eligibility for Scripps. Many of the strongest competitors are 8th graders on their third or fourth trip to regionals. The 2026 Scripps champion, Shrey Parikh, was a 14-year-old 8th grader who had been a finalist two years earlier.

**The honest truth:** Most school-level spellers won't make it past regionals, and that's completely normal. Only about 250 students reach the national Scripps finals out of millions who participate at the school level. The value is in the journey — the vocabulary gained, the study habits built, the confidence from performing on stage.`
      },
      {
        heading: "How to Prepare — What Actually Works",
        content: `### The Official Study Materials (start here — they're free)

- ***Words of the Champions*** — Scripps' own 4,000-word study guide, organized by difficulty. This is the source for preliminary and early rounds. If your child masters this list, they'll be well-prepared through school and often through regional bees. Download it free from spellingbee.com after your school enrolls.
- **School Spelling Bee Study List** — A 450-word subset of *Words of the Champions*, designed for classroom and school-level bees.
- **NSF practice words** — 1,000 words provided after registration. Good parallel practice.

### Study Methods That Work

**Root words and etymology** — This is the single most important technique for advancing beyond school-level bees. English borrows from dozens of languages, and each has patterns:
- Latin roots: "-tion," "-ment," "-ible" / "-able"
- Greek roots: "ph" for "f" sound, "psych-," "chron-"
- French origins: "-ette," "-esque," "-eau"
- German/Dutch: "-stein," "sch-" combinations

Once your child recognizes that a word comes from Greek, they can predict its spelling patterns even if they've never seen it before. This is how elite spellers handle words from the Unabridged Dictionary.

**Ask the right questions** — In competition, spellers can ask for the definition, part of speech, language of origin, alternate pronunciations, and use in a sentence. Practicing *how* to use these clues is as important as memorizing words.

**Daily practice routine** — 15–30 minutes daily beats 2-hour weekend cramming. Use flashcards (physical or apps like Quizlet), have someone quiz you aloud, and write words down — the physical act of writing helps memory.

### Paid Resources

- **SpellPundit** — A popular online platform specifically for competitive spellers. Word lists, practice tests, and analytics. Subscriptions run roughly **$50–150/year** depending on the plan.
- **Hexco Academic** — Publishes study guides organized by language of origin and difficulty. Books are **$15–40 each**.
- **Spelling coaches and tutoring** — Some families hire private spelling coaches, typically **$50–100+/hour**. This is common among families aiming for nationals but absolutely not necessary for a great experience at school and regional levels.
- **Spelling Bee Ninja** (spellingbee.ninja) — Free online tool with practice modes and word lists.`
      },
      {
        heading: "What It Costs — The Real Numbers",
        content: `Spelling bees are among the most affordable academic competitions. Here's what families actually spend:

| Item | Cost |
|---|---|
| Scripps (through school) | Free to students ($199 paid by school) |
| Scripps (homeschool) | $135 per family |
| SASB Regional | $50 per speller |
| SASB SAS-Bee (wildcard) | $75 application + $250 if selected |
| NSF Regional | $40 per contest |
| NSF National Finals | $60 |
| 98thPercentile Bee | Free |

### Total Annual Spend by Level

**Casual participant (school bee only):** $0. Your school's enrollment covers everything.

**Active competitor (Scripps + NSF + SASB):** $90–150/year in registration fees. Add $50–100 for study materials. Total: **$140–250/year**.

**Serious contender (adding coaching/resources):** Registration fees + SpellPundit subscription + study guides + optional tutoring: **$500–2,000+/year**.

**If your child reaches Scripps Nationals:** Travel and lodging are covered by Scripps for the speller and one guardian. You'd only pay for additional family members who want to attend.

**Bottom line:** A student can compete in three different spelling bees for under $150/year. The investment is time and effort, not money.`
      },
      {
        heading: "The South Asian Connection",
        content: `Let's talk about the elephant in the room: Indian-American kids have dominated the Scripps National Spelling Bee for three decades. **31 of the last 37 Scripps champions have been of Indian heritage.** Every single winner since 2008 has been Indian-American. In the 2026 finals, 5 of 9 finalists came from Indian immigrant families.

This isn't an accident, and it's not about any inherent advantage. It's about community infrastructure:

- **A culture of preparation.** Indian-American families tend to start early, study systematically, and treat spelling bees as a serious pursuit — not just a school activity.
- **Community networks.** WhatsApp groups, parent study circles, and informal coaching networks share word lists, study tips, and motivation. When your child sees friends and cousins competing, it normalizes the effort.
- **Organizations built for the community.** The South Asian Spelling Bee and North South Foundation exist specifically because the community invested in building competition infrastructure. NSF alone has 75+ chapters across the US.
- **A proven pathway.** When families see kids from similar backgrounds succeeding at the highest level, it creates a virtuous cycle of participation and aspiration.

This community strength is something to celebrate — and to leverage. If you're an Indian-American parent, chances are someone in your circle has navigated this path and can share practical advice.

But it also creates pressure. Not every kid from an Indian family wants to do spelling bees, and that's perfectly fine. The community's success shouldn't become an obligation for your child.`
      },
      {
        heading: "The Honest Take — Is This Right for Your Child?",
        content: `### Signs your child might love spelling bees
- They're a voracious reader who notices unusual words
- They enjoy word games, crossword puzzles, or Wordle
- They're curious about *why* words are spelled the way they are
- They don't mind memorization — or even find it satisfying
- They can handle being on stage (or want to learn how)

### Signs to reconsider
- They're doing it because everyone else in the community is
- They get deeply upset by making mistakes in front of others
- They hate memorization and prefer creative or hands-on activities
- The preparation feels like punishment, not practice

### The pressure conversation
In communities where spelling bees are popular, there's real social pressure to participate and excel. Kids hear about who made regionals, who went to nationals, who won trophies. For some children, this motivates them. For others, it creates anxiety and a sense of inadequacy.

Watch for these burnout signs:
- Crying or refusing to study before competitions
- Anxiety that disrupts sleep or school performance
- Tying their self-worth to competition results
- Losing interest in reading — the thing that usually feeds spelling ability

### Our honest advice
Let your child try a school spelling bee or a low-stakes community bee first. If they come home excited and ask to study more words, you have your answer. If they shrug and say it was fine, maybe spelling isn't their thing — and that's okay. There are dozens of other ways for a bright kid to develop discipline, vocabulary, and confidence.

The kids who go furthest are almost always the ones who genuinely enjoy words. The ones who ask "where does this word come from?" before asking "how do I spell it?" You can't force that curiosity, but you can nurture it by reading together, playing word games, and making language fun long before any competition enters the picture.`
      },
      {
        heading: "Key Dates to Know (2026–2027 School Year)",
        content: `| Event | Key Date |
|---|---|
| Scripps school enrollment opens | August 2026 |
| Scripps early bird enrollment deadline | Late September 2026 |
| Scripps enrollment deadline | January 30, 2027 |
| NSF Regional contests | Spring 2027 (chapter-specific) |
| Scripps Regional bees | February–March 2027 |
| SASB Virtual Regionals | Spring 2027 (check southasianspellingbee.com) |
| NSF National Finals registration opens | June 2027 |
| Scripps Bee Week (Nationals) | Late May 2027 |
| NSF National Finals | Summer 2027 |

**Pro tip for new families:** The school enrollment deadline in January is the hardest one to recover from if you miss it. If your school isn't enrolled in Scripps, talk to a teacher or administrator in September — don't wait. For NSF and SASB, registration typically opens a few months before regionals and fills up, so sign up early.

*Dates shown are approximate for the 2026–2027 cycle. Check official websites for the most current information: [spellingbee.com](https://spellingbee.com) for Scripps, [northsouth.org](https://northsouth.org) for NSF, [southasianspellingbee.com](https://southasianspellingbee.com) for SASB.*`
      }
    ]
  },
  {
    topic: "robotics",
    slug: "getting-into-robotics",
    title: "Getting Into Robotics",
    icon: "🤖",
    summary: "FIRST LEGO League, VEX, and beyond — the robotics competition landscape, costs, team structure, and how to get started from elementary through high school.",
    sections: [
      {
        heading: "Why Robotics?",
        content: `If there's one extracurricular that makes kids feel like they're building the future, it's robotics. And unlike most academic competitions, robotics is genuinely a team sport — your child will learn to collaborate, divide work, handle deadlines, and deal with things breaking at the worst possible moment.

What kids actually gain:

- **Engineering thinking.** Robotics forces kids to go from idea to working machine. They learn to design, prototype, test, fail, and iterate — the actual engineering process, not a textbook version of it.
- **Coding with a purpose.** Programming a robot to follow a line or pick up an object is more motivating than coding exercises on a screen. Kids learn logic, sensors, and control systems because they can *see* their code working (or not).
- **Teamwork under pressure.** Competition day means debugging a robot that worked perfectly at home but now refuses to cooperate. Kids learn to problem-solve together, stay calm, and adapt — skills that transfer to everything.
- **Presentation and communication.** Most robotics programs include judging sessions where teams present their engineering process, innovation projects, and team dynamics. This builds confidence and public speaking ability.

The scale of competitive robotics has grown enormously. **FIRST** (For Inspiration and Recognition of Science and Technology) alone now involves over **350,000 students** on more than **32,600 teams** worldwide. In 2026, the FIRST Robotics Competition fielded **3,724 teams** across 30 countries, with an estimated **93,500 high school students** participating. VEX Robotics runs a parallel ecosystem of similar scale. Robotics is no longer a niche — it's one of the biggest STEM activities in the country.`
      },
      {
        heading: "The Competition Landscape",
        content: `There are two major ecosystems — **FIRST** and **VEX** — plus a handful of smaller programs. Here's how they break down.

### FIRST Programs (the dominant ecosystem)

**FIRST LEGO League (FLL)** — The most popular entry point. Teams of up to 8 students build autonomous robots using LEGO kits to complete missions on a themed playing field in 2.5-minute matches. There's also an innovation project where teams research a real-world problem and present a solution.

- **Grades K–2:** Introduction to STEM concepts through guided building. Registration: **$250** for an 8-student team. Non-competitive showcase format.
- **Grades 3–5:** Hands-on building and basic coding. Registration: **$285** for 8 students. Participate in showcase festivals.
- **Grades 6–8 (Challenge):** The competitive tier. Registration: **$425** for 8 students. Teams compete at regional qualifiers with the chance to advance to state and world championships.
- **Required kits:** LEGO Education Computer Science & AI kits ($340–$2,249 depending on configuration) plus an annual game set (~$35). Kits are reusable year to year.
- **Time commitment:** 1.5–3 hours/week from September through competition in December–March.
- **Note:** The 2026–2027 BIOGLOW season will be the final season of the current FLL format. FIRST is transitioning to "Future Edition" with new technology.

**FIRST Tech Challenge (FTC)** — The step up from FLL. Teams of **8–15 students in grades 7–12** design, build, and program robots using more advanced hardware (metal, motors, sensors, Android-based control systems). Robots compete in alliance-based matches on a 12' × 12' field.

- **Registration:** **$325** per team per season.
- **Starter robot investment:** ~**$1,500** (driver kit $295, control hub $350, build kit $660). Many parts are reusable.
- **Total startup cost:** ~**$1,800** for a new team. Returning teams spend ~$500–1,000/year.
- **Season:** Kickoff in September, scrimmages November, qualifying tournaments January, state championships February, World Championship in April.
- **Why it's popular:** FTC hits a sweet spot — more technical than FLL but far more affordable and manageable than FRC. Robot fits in an 18"×18"×18" cube. Teams can operate out of a classroom, garage, or basement.

**FIRST Robotics Competition (FRC)** — The big leagues. Teams of **10–30+ students in grades 9–12** build industrial-sized robots (up to 125 lbs) with real motors, pneumatics, and vision systems. This is serious engineering with professional-grade tools and adult mentors who are often working engineers.

- **Registration:** **$6,500** per team per season (includes Kit of Parts and one regional event).
- **Total budget:** Rookie teams should plan for **$15,000–$20,000**. Veteran teams commonly spend **$30,000–$50,000+** including additional events, travel, and custom parts.
- **Season:** Kickoff in January, followed by an intense **6-week build season** where the robot must be designed, built, and tested. Regional competitions begin in late February.
- **Time commitment:** During build season, expect 15–25+ hours/week. It's essentially a part-time job. Many teams meet 4–5 days a week.
- **Why it matters:** FRC is the most prestigious youth robotics program in the world. It opens doors to engineering scholarships, and FIRST alumni get access to exclusive college and career opportunities.

### VEX Robotics (the other major ecosystem)

**VEX IQ** — For elementary and middle school students. Teams build robots using snap-together plastic components (no tools needed). Competitions include both teamwork challenges (two teams cooperate) and individual robot skills runs.

- **Registration:** **$200** per team (US).
- **Starter kit:** ~**$400–$500** for a VEX IQ kit.
- **Event fees:** ~$50–75 per tournament.
- **Great for:** Younger kids (grades 3–8) who want to build and compete without the LEGO ecosystem.

**VEX V5 Robotics Competition (V5RC)** — For middle and high school students. More advanced metal construction with motors, sensors, and custom programming. Alliance-based gameplay similar to FTC.

- **Registration:** **$200** per team.
- **Starter kit:** ~**$600–$900** for a V5 kit.
- **Event fees:** ~$50–75 per tournament.
- **How it compares to FTC:** VEX has more tournaments available (easier to find events) and a lower cost of entry. FTC has a more open design ecosystem and uses industry-standard programming.

### Other Programs Worth Knowing

- **RoboCup Junior** — International competition with divisions in soccer, rescue, and onstage performance. Less common in the US but popular globally.
- **BotBall** — Autonomous robot challenge for middle and high school teams. Smaller community but well-regarded.
- **Wonder League (by Wonder Workshop)** — For grades 1–6 using Dash and Dot robots. Fully virtual competition. Good for very young beginners.`
      },
      {
        heading: "The Typical Path — What's Realistic",
        content: `**Grades K–3: Exploration.** At this age, the goal is just to see if your child likes building and problem-solving with robots. FIRST LEGO League (K–2) and VEX IQ are gentle introductions. At-home kits like LEGO SPIKE Essential or Wonder Workshop's Dash robot are great for exploring without committing to a team.

**Grades 4–6: Getting Serious.** This is when most kids join their first real team. FLL Challenge (grades 3–5 and 6–8) or VEX IQ are the main options. Kids learn to work on a team, follow a season schedule, and experience the excitement of competition day. Many schools have teams; if yours doesn't, community teams are easy to find or start.

**Grades 7–9: The Transition.** Students who love robotics typically move from FLL to FTC or from VEX IQ to VEX V5. This is a significant step up in complexity — real programming, metal construction, strategic gameplay. Some students also start exploring FRC teams as freshmen.

**Grades 9–12: The Full Experience.** FRC is the pinnacle for students willing to make the commitment. The 6-week build season is intense but transformative. Students who go through FRC often describe it as the most impactful experience of their high school years — more than any class. Students who prefer a less time-intensive option stick with FTC or VEX V5.

**The honest truth:** Not every robotics kid needs to do FRC. FTC and VEX V5 offer excellent experiences with much less time and money required. The "right" level depends on your child's interest, your family's capacity, and what teams are available nearby. A student who does FLL through 8th grade and FTC through high school has had a fantastic robotics journey.`
      },
      {
        heading: "How to Get Started — Practical Steps",
        content: `### Finding a Team

- **FIRST team locator:** Go to firstinspires.org and use the "Find a Team" tool. Enter your zip code to see FLL, FTC, and FRC teams near you.
- **VEX team locator:** robotevents.com has a team finder.
- **Ask at school:** Many middle and high schools have robotics teams (often as after-school clubs). If your school doesn't have one, a teacher or parent can register a new team.
- **Community teams:** Libraries, community centers, and STEM organizations often host robotics teams. Some are affiliated with schools; others are independent.

### Starting a Team

If there's no team nearby, starting one is more doable than you'd think — especially for FLL and VEX IQ:
- You need **2 adult coaches** (no technical background required — you learn alongside the kids)
- Register on firstinspires.org or robotevents.com
- Order the required kit
- Find a meeting space (classroom, garage, library room)
- Recruit 4–8 kids

FIRST provides free coach training and a full curriculum. Many first-year coaches are parents who've never touched a robot before.

### At-Home Exploration (before or alongside a team)

- **LEGO SPIKE Essential** (ages 6+) — $359. The same platform used in FLL.
- **LEGO SPIKE Prime** (ages 10+) — $399. Used in FLL Challenge.
- **VEX GO** (ages 6+) — ~$250. Classroom-oriented snap-together kit.
- **Wonder Workshop Dash** (ages 6+) — ~$150. Friendly coding robot, good for beginners.
- **Arduino/Raspberry Pi projects** (ages 12+) — $30–80. For self-directed learners who want to go deeper into electronics and programming.

### Parent Involvement

Robotics is probably the most parent-involved STEM activity. Unlike math competitions where you drop off your kid, robotics teams actively need adult help:
- **Coaches:** Lead the team, manage logistics, guide (not do) the work.
- **Mentors:** Engineers, programmers, or other professionals who provide technical guidance.
- **Volunteers:** Event day needs referees, judges, field resetters, and logistics help.

If you have any engineering or technical background, your help will be especially valued. But even without it, teams always need people to handle logistics, fundraising, and team management.`
      },
      {
        heading: "What It Costs — The Real Numbers",
        content: `Let's be straightforward: robotics can be expensive. But the range is wide, and there are ways to participate affordably.

| Program | Registration | Startup Equipment | Annual Cost (Returning) |
|---|---|---|---|
| FLL (K–2) | $250/team of 8 | $340–$2,249 (kits) | ~$35 (annual set) |
| FLL (3–5) | $285/team of 8 | $340–$2,249 (kits) | ~$35 (annual set) |
| FLL Challenge (6–8) | $425/team of 8 | $340–$2,249 (kits) | ~$35 (annual set) |
| FTC | $325/team | ~$1,500 (robot parts) | $500–$1,000 |
| FRC | $6,500/team | $5,000–$15,000 (parts + tools) | $10,000–$50,000+ |
| VEX IQ | $200/team | $400–$500 (kit) | $200 + events |
| VEX V5 | $200/team | $600–$900 (kit) | $200 + events |

**Per-student costs** matter more than team totals:
- **FLL:** $50–200/student depending on team size and kit sharing.
- **FTC:** $200–500/student for a typical team.
- **FRC:** $500–2,000+/student for a well-funded team (often offset by sponsorships).
- **VEX:** $100–300/student.

### Grants and Sponsorships

- **FIRST team grants:** FIRST distributes grants from corporate sponsors (Qualcomm, Google, John Deere, etc.). New and underserved teams are prioritized.
- **VEX fee waivers:** Schools and nonprofits with 6+ teams may qualify for registration fee waivers.
- **Corporate sponsorships:** FRC teams commonly approach local businesses for sponsorships. Many companies have STEM sponsorship budgets.
- **DonorsChoose:** Teachers can create projects to fund robotics equipment.

**Bottom line:** FLL and VEX IQ are very affordable — comparable to a sport registration fee. FTC is moderate. FRC is a significant financial commitment but most teams fundraise heavily to cover it.`
      },
      {
        heading: "The South Asian Community Connection",
        content: `Indian-American families have embraced robotics as a natural extension of the community's strong STEM orientation. While there's no single "South Asian Robotics Bee" equivalent, the participation is substantial and growing.

**What you'll notice:**
- In the Bay Area, many FLL and FTC teams have significant South Asian participation — both as students and as parent coaches/mentors.
- Indian-origin engineers are heavily represented among adult mentors, bringing professional expertise to teams.
- Community organizations and temples sometimes sponsor or host robotics teams.
- WhatsApp parent groups are a common way families find teams and share information about registrations and events.

**The advantage for your family:** If you're in a tech-heavy area like the Bay Area, Seattle, or Austin, there's likely a robotics team nearby with families from similar backgrounds. The parent-mentor model means your professional network can directly benefit your child's team.

**A note on team culture:** One thing that makes robotics special is its emphasis on *Gracious Professionalism* — FIRST's principle that teams should compete fiercely but treat each other with respect. Teams regularly help competitors fix their robots. If your child has only experienced individual academic competitions, the collaborative culture of robotics can be a welcome change.`
      },
      {
        heading: "The Honest Take — Is This Right for Your Child?",
        content: `### Signs your child might love robotics
- They build things for fun — LEGO, cardboard, anything they can get their hands on
- They're curious about how machines work (taking things apart is a good sign)
- They enjoy working with others on projects
- They can handle frustration — robots break, code fails, things don't work the first (or fifth) time
- They like both the technical and creative sides of problem-solving

### Signs to reconsider
- They strongly prefer working alone — robotics is fundamentally a team activity
- They're already overcommitted — adding FTC or especially FRC to a packed schedule can lead to burnout
- They want instant gratification — robotics rewards patience and iteration
- They (or you) aren't ready for the time commitment, especially for FRC

### The time commitment conversation
This is the big one. Be honest with yourself about what your family can handle:
- **FLL:** 1.5–3 hours/week for ~5 months. Very manageable.
- **FTC:** 3–6 hours/week for ~7 months. Moderate commitment.
- **FRC:** 15–25+ hours/week during the 6-week build season, plus ongoing meetings. This is a *major* commitment that affects the whole family — evening and weekend schedules, driving to the workshop, volunteering at events.

Many FRC parents describe it as "the sport you didn't expect." It can be incredibly rewarding, but go in with eyes open about the time and energy involved.

### Team dynamics matter
Unlike individual competitions, your child's experience in robotics depends heavily on the team they're on. A great team with good mentors and a positive culture can be life-changing. A poorly run team with checked-out mentors or cliquey dynamics can be miserable. Before committing:
- Visit the team during a meeting
- Talk to other parents
- Ask how work is divided (does everyone get hands-on time, or do a few kids dominate?)
- Check if the team has a track record of student retention`
      },
      {
        heading: "Key Dates to Know (2026–2027 Season)",
        content: `| Program | Registration Opens | Season Starts | Key Competition Dates |
|---|---|---|---|
| FLL (all divisions) | May 2026 | August–September 2026 | Regionals: Nov–Mar / Worlds: Apr 2027 |
| FTC | May 2026 | September 2026 (Kickoff) | Qualifiers: Nov–Jan / States: Feb / Worlds: Apr 2027 |
| FRC | May 2026 | January 2027 (Kickoff + 6-week build) | Regionals: Late Feb–Apr / Worlds: Apr 2027 |
| VEX IQ | June 2026 | Varies by region | Tournaments: Oct–Feb / States: Feb–Mar / Worlds: Apr–May 2027 |
| VEX V5 | June 2026 | Varies by region | Tournaments: Oct–Feb / States: Feb–Mar / Worlds: Apr–May 2027 |

**Pro tip:** Registration fills up fast, especially for popular local events. Register your team in May–June if possible. For FLL, many regions cap the number of teams at qualifiers, and late registrants may not get a competition slot.

**For parents exploring options:** Attend a local robotics competition as a spectator first. FIRST and VEX events are free to watch and incredibly exciting. Seeing the energy, the teamwork, and the robots in action is the best way to decide if this is right for your family. Find events at firstinspires.org or robotevents.com.

*Check official websites for the most current information: [firstinspires.org](https://firstinspires.org) for all FIRST programs, [robotevents.com](https://robotevents.com) for VEX competitions.*`
      }
    ]
  },
  {
    topic: "chess",
    slug: "chess-for-kids",
    title: "Chess for Kids — Why It Matters",
    icon: "♟️",
    summary: "How chess builds critical thinking, the tournament path from local to nationals, and finding the right chess program for your child.",
    sections: [
      {
        heading: "Why Chess?",
        content: `Chess is one of the few activities where a six-year-old can sit across from an adult and compete on equal terms. No physical advantage, no head start — just thinking.

What kids actually gain from chess goes well beyond the board:

- **Pattern recognition and calculation.** Chess trains the brain to spot patterns, think several moves ahead, and evaluate trade-offs. These are the same skills that show up in math, coding, and strategic thinking of any kind.
- **Focus and patience.** A tournament game can last 2–4 hours. Learning to concentrate that long — without a screen, without prompts — is increasingly rare and increasingly valuable.
- **Handling wins and losses gracefully.** In chess, you lose. A lot. Even the best players in the world lose regularly. Learning to shake hands, analyze what went wrong, and come back stronger is one of the most important life skills chess teaches.
- **Independent decision-making.** Unlike team sports, there's no coach calling plays. Your child sits alone and makes every decision. That autonomy builds confidence.

The numbers reflect a surge in popularity. An estimated **35 million Americans** play chess regularly, and platforms like Chess.com have over **7 million members in California alone**. The "Queen's Gambit effect" and the rise of online chess during the pandemic brought millions of new players — and many of them were kids. Youth chess tournaments across the US are bigger and more competitive than ever.

For Indian-American families specifically, chess carries an extra charge of excitement right now. India's **Gukesh Dommaraju** became the youngest World Chess Champion in history in December 2024 at just 18 years old, and he's defending his title in Geneva in November 2026. More on that later — but the point is, this is a golden era for chess, and especially for Indian chess.`
      },
      {
        heading: "The Competition Landscape",
        content: `Chess competitions are organized around a rating system. Understanding that system is the key to understanding the whole landscape.

### How Ratings Work

The **US Chess Federation (USCF)** assigns every tournament player a numerical rating. You start as "unrated," and your rating goes up when you win and down when you lose. The amount it changes depends on your opponent's rating — beating a higher-rated player earns you more points.

Here's what the numbers roughly mean:
- **Under 600:** Beginner — knows the rules, still learning basic tactics
- **600–1000:** Developing player — understands basic openings and tactics
- **1000–1400:** Intermediate — solid club-level player
- **1400–1800:** Advanced — competitive at state level
- **1800–2000:** Expert territory — top scholastic players
- **2000+:** Candidate Master and above — seriously strong
- **2200+:** National Master — elite

Most scholastic players fall in the 400–1200 range, and that's perfectly fine. A rating of 1000 means your child is a solid, competent player.

### USCF Scholastic Tournaments

These are the bread and butter of youth chess in America.

**Local and regional tournaments** happen nearly every weekend in most metro areas. They're typically organized by chess clubs, schools, or state chess associations. Entry fees are usually **$20–50 per tournament**. Games are grouped by rating or grade level, so your child plays opponents of similar strength.

**State Championships** — Most states run an annual scholastic championship, divided by grade level (K–3, K–5, K–8, K–12 or similar). These are exciting, well-attended events and a great milestone to aim for. Entry fees are typically **$30–60**.

**National Scholastic Championships** — US Chess runs several major national events each year:
- **National K–12 Grade Championships** (December) — Players compete within their exact grade level
- **National High School Championship** (April)
- **National Junior High Championship** (April)
- **National Elementary Championship** (May)
- **All-Girls National Championship** — A growing event that's helped increase female participation

Entry fees for nationals range from **$105 (early bird) to $400 (on-site)**, so early registration saves a lot. Add travel, hotel, and meals, and a national tournament trip typically runs **$500–1,500** per family depending on location.

### Online Tournaments

Online rated tournaments have exploded in popularity. **Chess.com** and **Lichess** both run daily tournaments at every level. These are great for practice and for kids who don't have easy access to over-the-board events. Some online tournaments award USCF online ratings, though these are tracked separately from over-the-board ratings.

### FIDE Ratings

For serious players aiming at an international level, **FIDE** (the World Chess Federation) maintains a separate rating system. FIDE ratings are harder to earn (you need to play in FIDE-rated events) and carry more prestige internationally. Most scholastic players don't need to worry about FIDE ratings — that's for players pushing toward National Master and beyond.`
      },
      {
        heading: "The Typical Path — What's Realistic",
        content: `Chess is unusual because kids can start very young and progress is measurable through ratings. Here's a rough timeline:

**Ages 4–6: Introduction.** Many kids learn the rules around this age. Some start at school chess clubs, others from a parent or sibling. At this stage, the goal is simply to learn how the pieces move, basic checkmate patterns, and to enjoy the game. No tournaments needed yet — just play.

**Ages 6–8: First Tournaments.** If your child enjoys chess and wants to compete, this is a natural time to try a local scholastic tournament. The atmosphere is supportive (parents are everywhere), and most tournaments have an "unrated" or beginner section. Getting that first USCF rating — even if it's 300 — is exciting.

**Ages 8–11: Building Skills.** This is when most kids who enjoy chess start to take it more seriously. Regular practice, maybe a chess class or coach, and competing in 4–8 tournaments a year. A motivated child in this range might reach a 600–1000 rating, which puts them solidly in the competitive middle of scholastic chess.

**Ages 11–14: The Growth Spurt.** Players who stick with chess through middle school often see rapid improvement. This is when ratings can climb from 1000 to 1400+ with consistent work. State championships become meaningful, and national tournaments enter the picture.

**Ages 14–18: Serious or Social.** Some players push toward Expert (1800+) or National Master (2200+). Others play socially or on their school team. Both are great outcomes. The top scholastic players at this level are genuinely strong — competing with adults in open tournaments.

**The honest truth:** Most kids who play chess casually will settle into a 500–1000 rating. Kids who practice regularly and take lessons might reach 1200–1600. Reaching 2000+ requires serious dedication — typically years of study with a strong coach. And that's fine. A 900-rated kid who loves chess and plays in weekend tournaments is having a great experience.`
      },
      {
        heading: "How to Get Started — Practical Steps",
        content: `### School Chess Clubs

This is the most common entry point. Many elementary and middle schools have chess clubs, often run by a parent volunteer or an outside instructor. If your school doesn't have one, it's surprisingly easy to start — you need a volunteer coordinator, some chess sets, and a room. US Chess offers school affiliate memberships for **$40/year**, which lets you run rated tournaments.

### Local Chess Clubs

Search for chess clubs in your area through US Chess's club finder at uschess.org. Many clubs welcome kids, offer lessons, and run casual play nights. Some have dedicated scholastic programs. Monthly memberships at local chess clubs typically run **$30–80/month** for regular access to play, lessons, and tournament discounts.

### Online Platforms (the big three)

- **ChessKid** (chesskid.com) — Built specifically for kids under 13. Safe, moderated environment with lessons, puzzles, and games against other kids. Free basic access; Gold membership is **~$5–8/month** or **~$49/year**. This is the best starting point for younger kids.
- **Chess.com** — The world's largest chess platform. Lessons, puzzles, game analysis, tournaments. Free tier is generous; premium plans run **$5–14/month**. Better for kids 10+ who are ready for a bigger community.
- **Lichess** (lichess.org) — **100% free**, open-source, no ads, no premium tier. Excellent analysis tools, puzzles, and tournaments. Slightly less polished for beginners but beloved by serious players.

### Private Coaching

A good chess coach can accelerate improvement dramatically. Rates vary widely:
- **Online group classes:** $15–40/hour (shared with 4–8 students)
- **Online private lessons:** $30–80/hour for a strong amateur coach; $80–150+/hour for a titled player (National Master, International Master, or Grandmaster)
- **In-person private lessons:** Similar to online, sometimes higher

You don't need a coach right away. Start with free resources and a school club. If your child gets serious and hits a plateau (often around 800–1000), that's when coaching makes the biggest difference.

### Books for Beginners

- **Bobby Fischer Teaches Chess** (~$10) — A classic for absolute beginners. Pattern-based, no chess notation needed.
- **Winning Chess Tactics** by Yasser Seirawan (~$15) — Clear explanations of tactical patterns.
- **The Steps Method** workbooks — A structured curriculum used by many chess teachers, available by level.`
      },
      {
        heading: "What It Costs — The Real Numbers",
        content: `Chess is one of the most affordable competitive activities for kids. Here's what families actually spend:

### Membership
| Type | Cost |
|---|---|
| USCF Scholastic (under 15) | $17–25/year |
| USCF Youth (under 20) | $22–30/year |
| USCF Family Plan (all kids) | $50–80/year |

### Tournament Entry Fees
| Level | Cost |
|---|---|
| Local weekend tournament | $20–50 |
| State championship | $30–60 |
| National championship (early bird) | $105 |
| National championship (late/on-site) | $235–400 |

### Learning Resources
| Resource | Cost |
|---|---|
| ChessKid Gold (annual) | ~$49/year |
| Chess.com Premium | $5–14/month |
| Lichess | Free |
| Books | $10–20 each |
| Group coaching (online) | $15–40/hour |
| Private coaching | $30–150/hour |

### Total Annual Spend by Level

**Casual player (school club + occasional tournament):** USCF membership + 2–3 local tournaments + ChessKid: **$100–200/year**.

**Active competitor (monthly tournaments + online study):** Add more tournaments, maybe a chess.com subscription, a book or two: **$300–600/year**.

**Serious player (coaching + state/national events):** Weekly lessons + monthly tournaments + one national event: **$1,500–4,000+/year**, primarily driven by coaching costs and travel.

**Bottom line:** Your child can play in rated USCF tournaments, earn a national rating, and use world-class online training tools for under $200/year. Chess might be the best value in all of kids' competitive activities.`
      },
      {
        heading: "The Indian Connection — A Golden Era",
        content: `If there was ever a time to be excited about chess as an Indian-American family, this is it.

In December 2024, **Gukesh Dommaraju** — an 18-year-old from Chennai — became the youngest World Chess Champion in history, dethroning China's Ding Liren and breaking Garry Kasparov's 39-year-old record. He'll defend his title against Uzbekistan's Javokhir Sindarov in Geneva in November 2026.

But Gukesh isn't alone. India is producing a remarkable generation of chess talent:
- **R. Praggnanandhaa** (20) — Won the 2025 Tata Steel tournament and 2026 Norway Chess, qualified for the 2026 Candidates Tournament. He and his sister Vaishali are the first siblings to both earn Grandmaster titles.
- **Arjun Erigaisi** (22) — One of the world's top-ranked players.
- **Nihal Sarin** (21) — Another prodigy who earned the GM title at 14.
- And the legend himself, **Viswanathan Anand** — five-time World Champion and now FIDE's interim president — continues to inspire from the administrative side.

India won its **first-ever Chess Olympiad gold** in 2024, and the country now has more active grandmasters than almost any nation in the world.

For Indian-American kids, this matters because:
- **Role models who look like them.** Seeing Gukesh and Pragg on the world stage makes chess feel like *their* game.
- **Community infrastructure.** Indian-American communities in the Bay Area, New Jersey, Texas, and other hubs have strong chess cultures — informal tournaments, parent networks, and connections to coaching resources.
- **Cultural fit.** Chess aligns with values many Indian families hold: intellectual growth, discipline, strategic thinking. And unlike many activities, it doesn't require expensive equipment or a specific body type.

The excitement around Indian chess is real and growing. If your child shows an interest, there's never been a better time to nurture it.`
      },
      {
        heading: "The Honest Take — Is This Right for Your Child?",
        content: `### Signs your child might thrive in chess
- They enjoy strategy games, puzzles, or anything that requires thinking ahead
- They can sit still and focus for extended periods (even 30 minutes is a good start for young kids)
- They handle losing without falling apart — or are willing to learn how
- They're curious and want to understand *why* something works
- They enjoy one-on-one competition (chess is an individual sport)

### Signs to think twice
- They strongly prefer team activities and don't enjoy individual competition
- Sitting still for long periods is genuinely difficult for them (tournament games can be 1–4 hours)
- They get deeply frustrated by losing and take it personally — chess involves a lot of losing, especially early on
- They're only doing it because a parent wants them to

### What to know about tournament days

This catches many families off guard: **chess tournament days are long**. A typical scholastic tournament has 4–5 rounds, each lasting 30–90 minutes, spread across a full day (8 AM to 5 PM is common). Your child will be mentally exhausted. Bring snacks, books, and patience. Many families treat it as a family outing — the non-playing parent or sibling explores the area while the player competes.

### The screen time question

Online chess is amazing for improvement, but it's still screen time. Set boundaries around how much online chess is okay on a school night versus a weekend. Playing 5-minute "blitz" games endlessly is fun but not great for long-term chess development or sleep schedules. Structured study (puzzles, lessons, analysis) is more productive than just playing game after game.

### The pressure angle

Chess ratings are a number, and numbers invite comparison. "What's your rating?" becomes the first question kids ask each other at tournaments. This can be motivating for some kids and anxiety-inducing for others. Watch for signs that your child is tying their self-worth to their rating number. A rating is a measure of current playing strength, not intelligence or value.

### Our advice

Start with a school chess club or ChessKid. See if the spark is there. If your child enjoys it, try a local tournament — the atmosphere at scholastic events is welcoming and fun. Let improvement happen naturally through play and puzzles before adding coaching. And remember: the goal isn't to produce the next Gukesh. The goal is a kid who loves thinking, handles adversity well, and has a lifelong game they can enjoy at any age.`
      },
      {
        heading: "Key Dates to Know (2026–2027 School Year)",
        content: `| Event | Typical Timing |
|---|---|
| USCF membership renewal | Anytime (annual from purchase date) |
| School chess club season | September – May |
| Local tournaments | Nearly every weekend year-round |
| State Scholastic Championships | Varies by state (typically Jan–Mar) |
| National K–12 Grade Championships | December 2026 |
| National High School / Junior High | April 2027 |
| National Elementary Championship | May 2027 |
| All-Girls National Championship | April 2027 |
| FIDE World Youth Championship | Summer 2027 (location TBD) |
| Gukesh vs. Sindarov World Championship | November 25 – December 15, 2026 (Geneva) |

**Pro tip:** Local tournament schedules vary widely by region. The best way to find events near you is through your state chess association's website or US Chess's tournament finder at uschess.org. In the Bay Area, the Mechanics' Institute Chess Club (San Francisco) and the Bay Area Chess organization run regular scholastic events.

**For new families:** Start with a local or school tournament before committing to travel events. Your child's first tournament should be low-stakes and fun — save the state and national championships for when they've played a few rated games and have a sense of their level.

*Check official websites for the most current information: [uschess.org](https://uschess.org) for US Chess tournaments and membership, [chesskid.com](https://chesskid.com) for kids' online play, and [lichess.org](https://lichess.org) for free practice.*`
      }
    ]
  }
];

export function getGuideByTopic(topic: string): KidsGuide | undefined {
  return GUIDES.find((g) => g.topic === topic);
}

export function getGuideBySlug(slug: string): KidsGuide | undefined {
  return GUIDES.find((g) => g.slug === slug);
}

export function getAllGuides(): KidsGuide[] {
  return GUIDES;
}

/** Topics that have full guide content */
export function getAvailableTopics(): Set<string> {
  return new Set(GUIDES.map((g) => g.topic));
}
