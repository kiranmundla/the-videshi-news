#!/usr/bin/env python3
"""NRI World Writer — 2026-05-31 12:00 UTC run"""
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


# ── Article 1: Scripps Spelling Bee 2026 ──────────────────────────────────────

article1_body = """Shrey Parikh stood at the microphone inside DAR Constitution Hall, drew a breath, and rattled off 32 words in 90 seconds. The previous spell-off record was 29. The 14-year-old from Rancho Cucamonga, California, didn't just win the 98th Scripps National Spelling Bee on May 28 — he dismantled it.

His final decisive word was "bromocriptine," a polypeptide alkaloid that mimics dopamine activity. Across the stage, 12-year-old Ishaan Gupta of Jersey City, New Jersey, had spelled 25 words correctly in the same lightning round — an outstanding performance by any measure, except when your opponent is setting records. Sarv Dharavane, a 12-year-old from Dunwoody, Georgia, finished third.

All three finalists are of Indian origin.

## The dynasty deepens

Parikh's victory marks the fifth consecutive year an Indian American has claimed the championship. Faizan Zaki won in 2025, Bruhat Soma in 2024, Dev Shah in 2023, and Harini Logan in 2022. But the pattern runs far deeper: children of Indian heritage have now won 31 of the last 37 editions of America's most prestigious spelling competition. Since Balu Natarajan's historic first victory by an Indian-origin speller in 1985, and especially after Nupur Lala's famous 1999 win — immortalized in the documentary "Spellbound" — there have been only five editions in nearly three decades where an Indian American did not take the title.

The numbers defy probability. Indian Americans make up roughly 1.5 percent of the U.S. population. They have won more than 80 percent of recent Spelling Bees.

## The quiet infrastructure behind the wins

What looks from the outside like natural aptitude is, in truth, the product of a remarkably organized subculture. Across the United States, Indian American families have built an informal but effective infrastructure around competitive spelling. Regional bees, private coaching networks, word lists circulated through community WhatsApp groups, and summer study programmes have turned the Bee circuit into a year-round undertaking for serious contenders.

The families involved tend to share a common set of values rooted in the diaspora experience: that education is both a shield and a ladder, that disciplined preparation matters more than innate talent, and that public competition — far from being something to fear — is a chance to prove yourself in a country that your parents chose but where you must still earn your place.

Parikh's own journey underscores the point. He first reached the national Bee in 2022, tying for 89th. In 2024, he tied for third. Last year, he fell ill with a virus at his local school bee and misspelled "calipers," ending his run at the earliest stage. He returned in 2026 — his final year of eligibility as an eighth-grader at Day Creek Intermediate School — and left no room for doubt.

"Right now I'm probably the happiest I've ever been," Parikh said after lifting the trophy. "At my school bee last year, I was really dejected. I had a really tough time, but I'm glad I was able to bounce back."

## Beyond the trophy

The prize package reflects the competition's growing prestige: $50,000 from Scripps, $2,500 and a reference library from Merriam-Webster, $1,000 in Delta Air Lines flight credits, and various travel packages. But the real reward, for many Bee families, is something less tangible: a moment when a child of immigrants stands on a national stage, in a language that may not have been spoken at their grandparents' dinner table, and commands it with precision that nobody in the room can match.

Parikh says he plans to pivot to competitive mathematics and tennis. Meanwhile, both Gupta and Dharavane retain their eligibility and are expected to return next year — extending a pipeline that shows no sign of slowing.

The Bee began in 1925. The Indian American chapter of its history began in 1985. At this point, the two stories are nearly inseparable."""


# ── Article 2: 2026 Soros Fellows ─────────────────────────────────────────────

article2_body = """Every spring, the Paul & Daisy Soros Fellowships for New Americans announces 30 graduate students — all immigrants or children of immigrants — who will each receive up to $90,000 for their studies. It is one of the most competitive merit-based awards in American higher education. This year's class was selected from a record-breaking pool of 3,070 applicants.

Among the 2026 fellows, Indian Americans are once again disproportionately represented — a pattern that has held for years and says something important about where the diaspora's next generation is heading.

## The fellows

**Arya Rao** grew up in rural Northern Michigan, the daughter of Konkani immigrants from India who served as local physicians. She entered Columbia University at 16, captained the water polo team, and graduated with top honours in biochemistry and computer science. Now enrolled in the joint Harvard Medical School and MIT MD/PhD programme, she works with professors Pardis Sabeti and Sangeeta Bhatia — both pioneers in their fields — to use evolution as a lens for therapeutic design. Her research deploys artificial intelligence to "read" genetic records and guide new clinical interventions. Outside the lab, she conducts and plays saxophone as assistant artistic director for the Longwood Chorus, an ensemble of healthcare professionals.

**Ananthan Sadagopan** was raised in Westborough, Massachusetts, by parents from Chennai who emphasised the Vedas, Tamil culture, and rigorous education. After winning a gold medal at the International Chemistry Olympiad, he graduated from MIT in just three years with degrees in chemistry and biology. He is now pursuing a PhD at Harvard, where his research bridges organic chemistry and biology.

**Ria Das**, an MIT alumna (class of 2021, with a master's in engineering in 2022), and **Ronak Desai**, an MD student in the Harvard-MIT Health Sciences and Technology programme, round out the Indian-origin fellows with MIT affiliations. **Avinash Vadali**, already a Soros fellow, will begin a PhD in condensed-matter physics at MIT this fall.

## What the pattern reveals

The Soros Fellowship was established in 1997 by Paul and Daisy Soros — themselves Hungarian immigrants — to honour the contributions of newcomers to American society. Over 28 years, it has provided more than $80 million in funding across fields from medicine and law to the arts and engineering.

Indian Americans have featured prominently in nearly every class. The reasons are structural rather than mysterious. India sends more graduate students to the United States than any other country. Indian-origin families in America tend to cluster in professional corridors — medicine, engineering, computer science, finance — that produce the kind of academic credentials the fellowship rewards. And the fellowship's eligibility criteria (immigrants, children of immigrants, DACA recipients, green card holders) map neatly onto a community where the majority of adults are either first- or second-generation Americans.

But the individual stories complicate the neat demographic narrative. Rao's parents were not Silicon Valley engineers — they were small-town physicians in rural Michigan. Sadagopan's family carried Tamil cultural traditions into a Massachusetts suburb. Each fellow navigated the particular tension of diaspora childhood: absorbing one culture at home and another at school, and eventually finding a way to synthesise the two.

## The pipeline keeps flowing

The broader significance is this: the Indian American community is now deep enough into its American chapter that its second generation is not merely succeeding in established fields but pushing into the frontiers of those fields. Rao is not just studying medicine — she is building AI tools that could reshape how diseases are treated. Sadagopan is not just completing a chemistry degree — he did it in three years at MIT and won an international gold medal along the way.

These are not stories of immigrant survival. They are stories of immigrant acceleration — of a generation that inherited the discipline and ambition of parents who left India and is now deploying those qualities at the highest levels of American academia.

The $90,000 fellowship is helpful. The signal it sends is more valuable: that the children of Indian immigrants continue to rank among the most promising young minds in the country, and that the pipeline — from weekend Tamil classes and kitchen-table homework sessions to Harvard labs and MIT lecture halls — is not merely intact. It is widening."""


# ── Article 3: Micron CEO Sanjay Mehrotra billionaire ─────────────────────────

article3_body = """When Sanjay Mehrotra co-founded SanDisk in 1988, he was a young engineer from Kanpur who had come to the United States to study at UC Berkeley. Nearly four decades later, he runs Micron Technology, one of the three companies that effectively control the world's memory chip supply. And as of this week, according to Forbes, he is a billionaire — his estimated fortune reaching $1.2 billion as Micron's market capitalisation pushed past $1 trillion.

The milestone is personal. It is also a marker of something larger: the emergence of Indian-origin executives at the commanding heights of American technology, in roles where their decisions shape global supply chains, not just product roadmaps.

## The AI tailwind

Mehrotra's fortune is a direct consequence of the artificial intelligence boom. Micron manufactures high-bandwidth memory (HBM) chips — the specialised components that AI servers and data centres consume in vast quantities. As companies from Microsoft to Meta have poured hundreds of billions into AI infrastructure, demand for Micron's products has surged. The company's stock has risen roughly 200 percent this year alone.

Micron's trajectory under Mehrotra has been deliberate. He took over as CEO in 2017, inheriting a company that was profitable but not yet positioned for the AI era. He steered investment toward HBM and advanced DRAM, made the case to major customers that Micron could compete with Samsung and SK Hynix on quality, and navigated the geopolitical minefield of U.S.-China semiconductor restrictions. In May 2025, Micron opened a $15 billion fabrication plant in Boise, Idaho — the first new memory fab built on American soil in decades, backed partly by CHIPS Act subsidies.

## The Indian CEO phenomenon

Mehrotra's ascent fits a pattern that has become almost unremarkable in its consistency. Indian-origin executives now lead 16 Fortune 500 companies, including Microsoft (Satya Nadella), Alphabet (Sundar Pichai), FedEx (Raj Subramaniam), and Vertex Pharmaceuticals (Reshma Kewalramani). Collectively, these CEOs oversee enterprises employing 2.7 million Americans and generating nearly $1 trillion in annual revenue, according to a recent Indiaspora report.

But Mehrotra's story has a particular texture. Unlike some Indian-origin tech leaders who rose through software and services, Mehrotra built his career in hardware — in the capital-intensive, cycle-prone semiconductor industry where patience, manufacturing expertise, and strategic positioning matter more than quarterly growth narratives. He holds over 70 patents. He has lived through the booms and busts of the chip industry for nearly 40 years.

## From Kanpur to a trillion-dollar company

Mehrotra was born in 1958 in Kanpur, Uttar Pradesh. He earned his bachelor's degree from the Birla Institute of Technology and Science, Pilani (BITS Pilani), and moved to the United States for graduate studies at UC Berkeley, where he received a master's in electrical engineering and computer science. He co-founded SanDisk (originally SunDisk) with Eli Harari, pioneering flash memory technology that would eventually become the storage medium for everything from smartphones to cloud servers. Western Digital acquired SanDisk for $19 billion in 2016; a year later, Mehrotra joined Micron.

The journey from BITS Pilani to a $1.2 billion net worth is not a rags-to-riches fable — Mehrotra's family background was middle-class and educated, not impoverished. What it represents, instead, is the long arc of a certain kind of Indian immigrant career: technical excellence applied with entrepreneurial instinct over decades, in an industry where there are no shortcuts.

## What it means for the diaspora

For Indian Americans watching from engineering departments, startup garages, and corporate cubicles, Mehrotra's milestone is both aspirational and instructive. The CEO of a trillion-dollar chipmaker is not a social media founder or a management consultant — he is an engineer who stuck with hardware, filed patents, and waited for the world to need what he could build.

That is a different model of success from the ones that dominate diaspora discourse, and it may be the more durable one."""


articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Shrey Parikh Just Won the Scripps Spelling Bee. Indian Americans Have Now Won 31 of the Last 37.",
        "subheadline": "The 14-year-old from Rancho Cucamonga shattered the spell-off record with 32 words in 90 seconds. The runner-up was also Indian American. So was the kid in third.",
        "slug": make_slug("scripps-spelling-bee-2026-shrey-parikh-indian-american-dominance"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian American families have built a remarkable informal infrastructure around competitive spelling — coaching networks, word lists, summer programmes — that reflects core diaspora values about education, discipline, and proving yourself in a country your parents chose.",
        "tags": ["nri", "diaspora", "indian-american", "education", "spelling-bee", "achievement"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com/international/shrey-parikh-wins-2026-scripps-national-spelling-bee-title/article-19455"},
            {"name": "Madhyamam Online", "url": "https://madhyamamonline.com/en/world/indian-american-teen-wins-2026-scripps-national-spelling-bee"},
            {"name": "GKToday", "url": "https://gktoday.in/topic/shrey-parikh-wins-2026-scripps-national-spelling-bee/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6345320/pexels-photo-6345320.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The 2026 Soros Fellows Are Out. The Indian American Pipeline Keeps Widening.",
        "subheadline": "From a record 3,070 applicants, the Paul & Daisy Soros Fellowships chose 30 graduate students. Indian Americans once again appeared in disproportionate numbers — and their stories reveal a generation moving from immigrant discipline to frontier research.",
        "slug": make_slug("soros-fellows-2026-indian-american-arya-rao-ananthan-sadagopan"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The fellowship's eligibility criteria — immigrants and children of immigrants — maps directly onto the Indian American community, and the fellows' stories reveal the synthesis of diaspora values (Tamil weekend classes, kitchen-table study sessions) with the highest levels of American academia.",
        "tags": ["nri", "diaspora", "indian-american", "education", "fellowship", "achievement", "soros"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Harvard GSAS", "url": "https://gsas.harvard.edu/news/rao-and-sadagopan-awarded-2026-soros-fellowship"},
            {"name": "MIT News", "url": "https://news.mit.edu/2026/six-from-mit-awarded-2026-paul-and-daisy-soros-fellowships-new-americans"},
            {"name": "MIT Physics", "url": "https://physics.mit.edu/news/six-from-mit-awarded-2026-paul-and-daisy-soros-fellowships-for-new-americans/"}
        ]),
        "score_total": 72,
        "status": "published",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/27300388/pexels-photo-27300388.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "body": article2_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Micron's Sanjay Mehrotra Just Became a Billionaire. His Path There Was Unusually Patient.",
        "subheadline": "The Indian-born CEO co-founded SanDisk, filed 70 patents, and spent four decades in the semiconductor industry before the AI boom turned Micron into a trillion-dollar company and his stake into a $1.2 billion fortune.",
        "slug": make_slug("sanjay-mehrotra-micron-billionaire-indian-ceo-semiconductor"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Mehrotra's career — from BITS Pilani to UC Berkeley to co-founding SanDisk to running a trillion-dollar chipmaker — represents a different model of Indian diaspora success: technical depth over quick exits, patience over velocity, hardware over software.",
        "tags": ["nri", "diaspora", "indian-american", "business", "technology", "ceo", "semiconductor"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Inshorts", "url": "https://inshorts.com/en/news/microns-indianorigin-ceo-sanjay-mehrotra-becomes-billionaire"},
            {"name": "Forbes", "url": "https://www.forbes.com/profile/sanjay-mehrotra/"},
            {"name": "Indiaspora Partners in Progress Report", "url": "https://indiaspora.org/report"}
        ]),
        "score_total": 70,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/de/Sanjay_Mehrotra_2025_%28cropped%29.jpg",
        "body": article3_body,
    },
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
