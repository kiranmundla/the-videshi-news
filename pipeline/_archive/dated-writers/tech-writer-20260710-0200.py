#!/usr/bin/env python3
"""Tech writer — 2026-07-10 02:00 PDT run. Two articles: Xbox/Asha Sharma + H-1B crackdown."""

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

# ─────────────────────────────────────────────────────
# ARTICLE 1: Xbox / Asha Sharma
# ─────────────────────────────────────────────────────

art1_body = """Asha Sharma was born in Eau Claire, Wisconsin, in 1989. She studied at Stanford. She spent years climbing through Microsoft's ranks, eventually running the company's CoreAI product organisation. None of that mattered to a significant slice of the internet when she announced, on 6 July, that she would cut roughly 4,800 jobs across Microsoft's gaming division — 3,200 of them from Xbox alone — in what she called "the most significant restructure in Xbox history."

The backlash was immediate and predictable. Critics online linked Sharma's Indian heritage to the layoffs, accusing her of replacing Americans with cheaper foreign labour. One widely shared thread framed the story as an Indian-origin CEO firing American workers while Microsoft sat as the sixth-largest sponsor of H-1B visas in the country — approved for 2,273 employer-sponsored non-immigrant workers this year alone. That Sharma was born and raised in the United States, that she had no role in Microsoft's visa sponsorship decisions, and that H-1B holders were also affected by the cuts — none of it registered.

Microsoft pushed back. "These decisions are based on business need, not visa status," a spokesperson said. "H-1B employees were also impacted by job eliminations in the U.S."

## The Business Case

Sharma's memo to staff was unusually blunt. "Our business today is not healthy," she wrote. "We are operating at margins that are 3-10x lower than comparable platform and publishing businesses." She laid the blame squarely on her predecessor, Phil Spencer, whose acquisition-heavy strategy — Activision Blizzard, Bethesda, and a string of smaller studios — left Xbox overstaffed and unfocused.

"In order to grow, we made a bunch of bets," Sharma told Fortune. "And as we did that, we inherently didn't focus on the core business. The number one measure of your strategy is what you put your resources behind, and we simply spread ourselves too thin."

The restructuring goes well beyond headcount. Four studios — Compulsion Games, Double Fine Productions, Ninja Theory, and Undead Labs — will be spun off to new management. Xbox console prices are rising, driven partly by component costs inflated by the global AI hardware boom. And the company is pivoting back to platform exclusivity, reversing Spencer's push to bring Xbox games to PlayStation and Nintendo.

## A Pattern That Keeps Repeating

The racial backlash against Sharma fits a well-documented pattern. Indian-origin executives at the helm of American companies face an extra layer of scrutiny that their peers rarely encounter. When Sundar Pichai announced layoffs at Google, when Satya Nadella cut teams at Microsoft's cloud division, the conversation briefly touched on their heritage before moving on. For Sharma — younger, less established in the public eye, and a woman — the identity-based attacks were more visceral and more sustained.

Rep. Riley Moore of West Virginia called for an end to the "H-1B scam" in response to the Xbox layoffs, a statement that conflated Sharma's American citizenship with the broader immigration debate. The timing was particularly charged: Vice President JD Vance had announced a major H-1B fraud investigation just a day earlier, and the Xbox story became a lightning rod for anxieties about foreign labour that have little to do with a CEO born in Wisconsin.

## What It Means for Indian-Americans in Tech

Sharma is now one of the most prominent Indian-American women in the gaming industry, leading a division that generates billions in revenue and shapes how 100 million people play. Her restructuring, if it works, could restore Xbox to financial health within two years. If it does not, she will be the face of its decline.

For Indian-Americans climbing the corporate ladder in tech, the message is familiar and disheartening: the scrutiny doubles at the top, and your name becomes the story before your strategy does. Sharma is not the first to navigate this. She will not be the last."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Xbox's Indian-American CEO Just Ordered the Biggest Restructuring in the Brand's History. The Internet Blamed Her Heritage.",
    "subheadline": "Asha Sharma, born in Wisconsin, is cutting 4,800 jobs and spinning off four studios to rescue Microsoft's gaming division. Online critics turned her ethnicity into the story.",
    "slug": make_slug("xbox-asha-sharma-restructuring-racist-backlash-indian-american"),
    "category": "technology",
    "vertical": "tech-leadership",
    "diaspora_angle": "An Indian-American woman leads one of tech's toughest turnarounds while facing identity-based attacks — a pattern that follows diaspora professionals to the top of corporate America.",
    "tags": ["microsoft", "xbox", "asha-sharma", "indian-american", "tech-leadership", "layoffs", "h1b"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox News", "url": "https://www.foxnews.com/politics/fury-erupts-us-brand-fires-1600-employees-after-securing-thousands-foreign-worker-visas"},
        {"name": "Polygon", "url": "https://www.polygon.com/analysis/xbox/588765/xbox-layoffs-too-big-to-fail"},
        {"name": "The Gamer", "url": "https://www.thegamer.com/xbox-ceo-blames-layoffs-phil-spencer-acquisitions/"},
        {"name": "The Sun", "url": "https://www.thesun.co.uk/tech/33984009/microsoft-to-axe-4800-jobs-as-part-of-restructure/"},
        {"name": "Bloomberg", "url": "https://www.bloomberg.com/news/articles/2026-07-07/microsoft-xbox-layoffs-exclusivity-strategy"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/62/Asha_Sharma_CEO_of_XBOX_at_2026_XBOX_Showcase.jpg",
    "image_caption": "Asha Sharma, CEO of Xbox, at the 2026 Xbox Showcase",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ─────────────────────────────────────────────────────
# ARTICLE 2: H-1B Crackdown
# ─────────────────────────────────────────────────────

art2_body = """Vice President JD Vance stood at a podium in Milwaukee on Wednesday and made the announcement that hundreds of thousands of Indian tech professionals in America had been dreading. The Department of Labor, he said, had launched "a major investigation" into H-1B visa fraud, firing off dozens of subpoenas as its opening salvo.

"American jobs ought to go to American workers and not foreign fraudsters," Vance said, flanked by Labor Department Inspector General Anthony D'Esposito. "The Department of Labor is fighting back against it."

The investigation is the Trump administration's first large-scale probe targeting the H-1B and PERM visa programmes — the two pathways that keep much of Silicon Valley's Indian workforce in the country. And if the scope of the rhetoric is any guide, it will not be the last.

## Cognizant Named, but Not Charged

D'Esposito went further than most expected. In an interview with Fox Business, he named Cognizant — the New Jersey-based IT services giant with 357,600 employees and $5.41 billion in quarterly revenue — as a company flagged by whistleblowers. "We have whistleblowers talking about some of the biggest companies, like Cognizant," he said, before clarifying that no formal charges had been filed and the company had not been accused of wrongdoing.

The timing is brutal for Cognizant. The company is already in the middle of "Project Leap," a restructuring programme that will cut 4,000 jobs and cost between $230 million and $320 million in severance, all in the name of pivoting to an AI-first operating model. Its CEO, Ravi Kumar S, has framed the cuts as a forward-looking bet on automation and outcome-based delivery. Being dragged into a federal fraud investigation — even tangentially — adds a reputational dimension the company did not need.

## The Numbers Behind the Probe

Department of Homeland Security assessments cited in the investigation suggest that as many as 21 per cent of H-1B petitions may be fraudulent. D'Esposito linked visa fraud to organised crime, claiming it fuels "violent crime" and is "tied to cartels" and "transnational gangs." While those claims are contested by immigration advocates, they signal the political framing the administration intends to use.

The technology sector remains the investigation's centre of gravity. Roughly 60 to 70 per cent of new H-1B approvals go to tech companies and IT services firms. Indian nationals account for 71 per cent of all approved H-1B beneficiaries — a concentration that makes any crackdown on the programme disproportionately an Indian story.

## The $100,000 Fee That Won't Die

Complicating the picture further: the legal status of President Trump's $100,000-per-petition fee for H-1B applications remains in limbo. A federal judge struck the fee down in June, ruling that the executive branch had overstepped by imposing what amounted to a tax — a power reserved for Congress. But the government has moved to keep the fee in place while it appeals.

For employers in education, healthcare, and technology — the sectors most reliant on international talent — the whiplash is paralyzing. Many had paused hiring pipelines when the fee was announced and are now unsure whether to restart them.

## What Is Coming Next

The investigation is just one piece of a broader regulatory offensive. According to the Department of Labor's published agenda, several new rules are imminent:

- **Higher fees for H-1B-dependent firms**: Companies where more than half the U.S. workforce holds H-1B or L-1 visas will pay an additional $4,000 for extension petitions, up from zero. This directly targets Indian IT outsourcing firms like TCS, Infosys, and Wipro.
- **Tighter third-party placement rules**: An August proposal will require employers to prove genuine employer-employee relationships at client sites — the model that underpins most of India's IT services exports to America.
- **Higher prevailing wages**: The DOL is drafting rules to raise minimum salary thresholds for H-1B positions and employment-based green cards.
- **H-4 EAD changes**: The DHS is expected to finalise a rule this month ending automatic extensions of work permits for H-4 visa holders — the spouses of H-1B workers. Roughly 100,000 Indian spouses could face gaps in work authorisation, losing income that often covers mortgages, childcare, and retirement savings.

## The Ground Is Shifting

For the 500,000-plus Indian professionals working in the United States on H-1B visas, and the families whose lives are built around them, the message from Washington is unmistakable: the rules are being rewritten, and the rewriting has begun. The investigation may ultimately find fraud where fraud exists. But the broader regulatory squeeze — higher costs, tighter scrutiny, vanishing spousal work rights — will reshape the economics of the Indian tech pipeline to America regardless of what any probe uncovers."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Washington Just Launched Its Biggest H-1B Fraud Investigation. Indian Tech Workers Are in the Crosshairs.",
    "subheadline": "VP Vance announced dozens of subpoenas, Cognizant was named by whistleblowers, and a $100,000 application fee is in legal limbo. Here is what every Indian professional in America needs to know.",
    "slug": make_slug("vance-h1b-fraud-investigation-cognizant-indian-tech"),
    "category": "technology",
    "vertical": "immigration",
    "diaspora_angle": "With 71% of H-1B holders being Indian nationals, this investigation and the regulatory squeeze that follows it directly threaten the livelihoods and families of hundreds of thousands of Indian tech workers in America.",
    "tags": ["h1b", "immigration", "cognizant", "jd-vance", "tech-workers", "indian-it", "visa-policy"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-its-first-major-h-1b-visa-fraud-investigation"},
        {"name": "NY Post", "url": "https://nypost.com/2026/07/09/us-news/vance-labor-watchdog-launch-immigration-fraud-probe-to-protect-american-jobs/"},
        {"name": "Bhaskar English", "url": "https://www.bhaskarenglish.in/international/news/us-indian-it-cognizant-h1b-visa-fraud-investigation-138397033.html"},
        {"name": "Bloomberg Law", "url": "https://news.bloomberglaw.com/daily-labor-report/h-1b-visa-fees-legal-whiplash-demands-employers-preparation"},
        {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/news/why-1-lakh-indian-h-4-visa-holders-could-face-job-disruptions-in-the-us"}
    ]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b5/Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg/1280px-Frances_Perkins_Building_of_the_United_States_Department_of_Labor_in_Washington%2C_D.C._-_8.jpg",
    "image_caption": "The Frances Perkins Building, headquarters of the U.S. Department of Labor in Washington, D.C., which is leading the H-1B fraud investigation",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

# ─────────────────────────────────────────────────────
# INSERT
# ─────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']} — {art['headline'][:70]}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
