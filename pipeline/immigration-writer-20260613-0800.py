#!/usr/bin/env python3
"""Immigration writer — 2026-06-13 08:00 UTC run"""
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


# ── Article 1 ──────────────────────────────────────────────────────────
article1_body = """Indian applications to American LL.M. programmes have dropped twenty-three per cent this year. Chinese applications fell twenty-one per cent. Across all nationalities, the applicant pool shrank fourteen per cent, according to the Law School Admission Council — the steepest contraction in years and one that law schools are struggling to explain away.

The numbers, reported by Reuters, come at a moment when the broader pipeline that moves Indian students from F-1 visas through OPT and into H-1B employment is showing cracks at every joint. And for the hundreds of thousands of Indian professionals already in the United States on work visas, these figures carry a warning: the system that brought them here is being quietly dismantled from the bottom up.

## The Rejection Machine

The context behind the LL.M. decline is blunt. In 2025, the United States denied sixty-one per cent of F-1 student visa applications from India — up from thirty-six per cent just two years earlier, according to Shorelight Education. For every hundred Indian students who applied for a visa to study in America, sixty-one were turned away.

The result has already shown up in enrolment data. India's government told Parliament in April that the number of Indian students in American institutions fell 6.9 per cent between February 2025 and February 2026 — from 378,787 to 352,644. That 26,000-student decline is the largest since the pandemic, but this time it is policy-driven, not virus-driven.

At UC Berkeley's law school, LL.M. applications are down twenty per cent. At Michigan, they dropped thirty per cent — after an eight per cent fall the previous year. Many of the largest programmes, including Columbia, NYU, Harvard, and Georgetown, declined to share their numbers.

## Why Law Schools Matter to the Immigration Pipeline

For Indian lawyers, an LL.M. from a US law school is not simply a credential. It is a gateway. The degree qualifies graduates to sit for the bar exam in several states, practice in American firms, and — critically — apply for OPT work authorisation and eventually enter the H-1B lottery.

Remove that gateway, and you remove a feeder channel into the American legal and corporate workforce. Indian lawyers working in US firms on H-1B visas already navigate a precarious path; a shrinking LL.M. pipeline means fewer will even get the chance to try.

"There is a feeling that the United States, generally speaking, is maybe not as welcoming to international students as it used to be," said Gisele Joachim, the Law School Admission Council's vice president for law school engagement.

The financial implications are not trivial for the schools either. LL.M. students typically pay full tuition — an average of $59,570 at private institutions — with far less financial aid than J.D. students. They are, in effect, a revenue stream that subsidises the rest of the law school. When that stream thins, programmes shrink, faculty positions disappear, and the international character of American legal education narrows.

## The Competition Problem

Even before the Trump administration's immigration crackdown, US law schools were losing ground to cheaper LL.M. programmes in Britain, Australia, and Europe. A one-year LL.M. at a top London university can cost half what an American programme charges, with fewer visa complications and a more straightforward path to post-study work.

"I've had people say to me, 'I always wanted to do an LL.M. in the states, but now I want to do it in the UK,'" said Sylvia Polo, an admissions consultant who previously ran LL.M. programmes at Columbia and the University of Miami.

For Indian students weighing the calculus — a sixty-one per cent visa rejection rate, tuition approaching $60,000, and an OPT programme whose future the USCIS director has openly questioned — the arithmetic increasingly favours London, Melbourne, or Berlin.

## What This Means for Indian Americans

The downstream effects are not abstract. Indians represent roughly thirty per cent of all foreign enrolments in the US, nearly half of all STEM-OPT participants, and about seventy-five per cent of H-1B visa recipients. They constitute the largest segment of immigrant doctors and nearly a quarter of tech workers in Silicon Valley with a bachelor's degree or higher.

Every constriction at the student visa stage ripples forward: fewer OPT applicants, fewer H-1B lottery entrants, fewer green card petitions, fewer eventual citizens. The pipeline does not break at one point — it thins everywhere at once.

For Indian Americans already established in the United States, the implications are generational. A smaller incoming cohort of Indian professionals means fewer peers, fewer mentors for the next wave, and a weaker collective voice in the policy debates that shape their own futures.

The question is not whether the trend will reverse. The question is whether anyone in Washington is paying attention to the fact that it exists."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "American Law Schools Are Losing India — and the Visa Pipeline May Never Recover",
    "subheadline": "Indian LL.M. applications dropped 23 per cent this year. With F-1 visa refusals at a decade high and enrolment falling for the first time since the pandemic, the student-to-H-1B pipeline is thinning at every stage.",
    "slug": make_slug("american-law-schools-losing-india-visa-pipeline"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The F-1 to OPT to H-1B pipeline that brings Indian professionals to the US starts with student enrolment — and that pipeline is breaking, with implications for every Indian American who arrived through it.",
    "tags": ["f1-visa", "llm", "student-visa", "opt", "h1b", "law-school", "india"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/us-law-schools-see-sharp-drop-international-student-applications-2026-06-12/"},
        {"name": "Inside Higher Ed / Shorelight", "url": "https://www.insidehighered.com/news/global/2026/04/22/f-1-student-visa-refusals-surged-2025"},
        {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/national/indian-student-enrolment-in-us-falls-nearly-7-amid-stricter-visa-rules/article69412345.ece"},
        {"name": "ICEF Monitor", "url": "https://monitor.icef.com/2026/04/visa-rejections-climb-in-the-us-for-international-students-from-key-markets-including-india/"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/29229903/pexels-photo-29229903.jpeg",
    "image_caption": "Graduates in academic gowns at a university commencement ceremony",
    "image_attribution": "Pexels",
    "body": article1_body,
}


# ── Article 2 ──────────────────────────────────────────────────────────
article2_body = """Three Indian seafarers are dead, killed when a US aircraft fired precision munitions into the engine room of the M/T Settebello in the Sea of Oman on Wednesday. Twenty-one others were rescued, some after jumping into the water. The ship, a Palau-flagged oil tanker transiting Iranian waters, was carrying no weapons.

A day earlier, twenty-four Indian sailors had been rescued from the M/T Marivex after a similar US strike. On Thursday, a third ship — the Guinea-Bissau-flagged M/T Jalveer, with twenty Indian crew aboard — was hit. All three attacks were part of Washington's blockade of Iranian ports, now in its third month.

For India's 300,000-strong merchant marine workforce, the deaths are not a geopolitical abstraction. They are a professional crisis. And for the Indian diaspora watching from the United States, the timing could not be worse: Prime Minister Narendra Modi is expected to meet President Donald Trump at the G7 summit in France this weekend, with H-1B visas and trade concessions at the top of the agenda.

## The Diplomatic Bind

India summoned Jason Meeks, the deputy chief of mission at the US Embassy in New Delhi, on Friday — the second formal protest in the same week. "The attacks that are happening must stop," said India's foreign ministry spokesperson Randhir Jaiswal. It was the strongest language New Delhi has used toward Washington since the Iran conflict began in March.

The problem is structural: India needs things from the United States that require goodwill. The two countries are negotiating the first tranche of a bilateral trade agreement, which India hopes will include preferential tariff treatment. Modi's government has signalled it will raise the H-1B issue directly — pushing back against the $100,000 application fee (recently struck down by a federal judge, now heading to Congress for codification) and the broader slowdown in visa processing that has left Indian workers in limbo.

But diplomatic capital is not infinite. Every formal protest over dead sailors is a conversation that displaces one about visa backlogs. Every front-page photograph of a grieving family in Deoria makes it harder for Modi to return from France with a handshake and no concrete deliverables.

"The attacks on Indian shipping and the deaths of three Indian sailors have already become an irritant in a wobbling relationship," said Kanti Bajpai, a political scientist and visiting senior fellow at India's Centre for Social and Economic Progress.

## The Opposition Smells Blood

India's Congress party seized on the deaths as evidence that Modi's "personal rapport" with Trump — long showcased as a diplomatic asset — has failed to protect Indian lives.

"The Prime Minister, who has repeatedly showcased his personal rapport with President Donald Trump as a diplomatic achievement, cannot evade responsibility when that relationship fails to protect Indian lives," Congress said in a statement.

The Centre of Indian Trade Unions demanded that Modi "speak — loudly and firmly." India's Forward Seamen's Union called the strikes a "gruesome attack" on "dedicated maritime professionals."

Modi has not publicly commented on the deaths. His ports and shipping minister, Sarbananda Sonowal, confirmed the killings and said the government "stands firmly with the bereaved."

## What This Means for Immigration Talks

The India-US relationship is the scaffolding on which every immigration concession rests. When the relationship is strong — as it was during the Quad summits, the defence technology agreements, the Rubio visit last month — there is room to negotiate on H-1B fees, green card backlogs, and consular appointment wait times.

When the relationship frays — over tariffs, over Pakistan, over dead sailors — that negotiating space contracts. An Indian government under domestic pressure to confront Washington over military strikes is not an Indian government that can afford to look like it traded dead sailors for visa quotas.

For the 730,000 Indian nationals on H-1B visas in the United States, and the hundreds of thousands more waiting in green card queues, the calculus is uncomfortable but clear: their immigration futures are entangled with geopolitics they cannot control. A ship attacked in the Sea of Oman is, in ways that matter, an event that affects a software engineer in Sunnyvale.

The G7 meeting begins on June 15. Modi departed India on Friday. He carries with him a list of immigration asks and three families' demands for their sons' bodies. Both will require answers from the same man."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "Three Dead Sailors, One H-1B Wishlist — Modi Goes to the G7 With Blood on the Agenda",
    "subheadline": "US forces killed three Indian seafarers in the Gulf this week. Now Modi must confront Trump over military strikes and negotiate visa concessions in the same meeting — and the diplomatic math does not add up.",
    "slug": make_slug("modi-g7-dead-sailors-h1b-diplomatic-bind"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The India-US relationship that governs H-1B visas, green card backlogs, and consular processing is now under strain from US military strikes that killed Indian civilians — complicating immigration diplomacy for 730,000 Indian workers in the US.",
    "tags": ["india-us-relations", "g7", "modi-trump", "h1b", "seafarers", "diplomacy", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "CNN", "url": "https://www.cnn.com/2026/06/12/india/india-seafarers-deaths-anger-analysis-intl-hnk"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indians-grieve-call-action-after-us-strike-kills-sailors-2026-06-12/"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indias-modi-trump-likely-meet-at-g7-discuss-trade-visas-source-says-2026-06-10/"},
        {"name": "New York Post", "url": "https://nypost.com/2026/06/12/us-news/us-disables-third-oil-tanker-trying-to-break-through-blockade-on-iran-ports/"}
    ]),
    "score_total": 85,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/36563588/pexels-photo-36563588.jpeg",
    "image_caption": "An oil tanker sailing on the open sea",
    "image_attribution": "Pexels",
    "body": article2_body,
}


# ── Insert ──────────────────────────────────────────────────────────
articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
