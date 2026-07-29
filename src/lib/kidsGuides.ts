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
