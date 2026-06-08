#!/usr/bin/env python3
"""NRI World Writer — 2026-06-08 06:00 UTC run"""
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
    # ──────────────────────────────────────────────
    # Article 1: Shrey Parikh wins Scripps Bee 2026
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "A 14-Year-Old From Rancho Cucamonga Just Spelled 32 Words in 90 Seconds. The Scripps Trophy Is His.",
        "subheadline": "Shrey Parikh set a new spell-off record to claim the 2026 Scripps National Spelling Bee title, continuing a decades-long streak of Indian-American dominance at the competition.",
        "slug": make_slug("shrey-parikh-scripps-spelling-bee-2026-indian-american-champion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian-American children have won 21 of the last 28 Scripps titles. Five of nine finalists this year were of Indian origin. The Bee has become one of the most visible stages for diaspora academic achievement.",
        "tags": ["nri", "diaspora", "education", "spelling-bee", "indian-american", "youth"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Scripps National Spelling Bee / Globe Newswire", "url": "https://in.tradingview.com/news/GlobeNewswire:7d84c5e8d094b:0/"},
            {"name": "Fox LA", "url": "https://www.foxla.com/"},
            {"name": "NPR / WAMC", "url": "https://www.wamc.org/"},
            {"name": "Wikipedia — 98th Scripps National Spelling Bee", "url": "https://en.wikipedia.org/wiki/98th_Scripps_National_Spelling_Bee"},
            {"name": "The Brighter World", "url": "https://thebrighterworld.com/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/f3/Scripps_National_Spelling_Bee_%2855301276503%29.jpg/1280px-Scripps_National_Spelling_Bee_%2855301276503%29.jpg",
        "image_caption": "The Scripps National Spelling Bee stage at DAR Constitution Hall in Washington, D.C.",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """When the silver podium and buzzer appeared on stage at DAR Constitution Hall in Washington, D.C. on May 28, a collective gasp swept the hall. Two spellers — both of Indian origin, both impossibly composed — had traded flawless rounds for the better part of two hours. The regular bee was over. What came next was a 90-second sprint that would crown a champion.

Shrey Parikh, a 14-year-old eighth-grader from Rancho Cucamonga, California, stepped to the microphone and tore through 32 words in a minute and a half. His opponent, 12-year-old Ishaan Gupta of Jersey City, New Jersey, spelled 25 correctly — a performance that would have won any prior spell-off. Parikh's total shattered the previous record of 29 set by Bruhat Soma in 2024.

His official winning word: *bromocriptine*, a polypeptide alkaloid that mimics dopamine. The kind of term that would send most adults to a dictionary and most teenagers to a therapist. Parikh barely paused before spelling it.

## Three years, three outcomes

This was not a debut performance. Parikh first appeared at the national bee in 2022, finishing tied for 89th. He returned in 2024 and placed third — close enough to taste it, far enough to sting. Then came a setback: he lost his school bee last year while battling a fever, a defeat he described as genuinely painful.

"Right now I'm probably the happiest I've ever been," he told reporters backstage. "At my school bee last year, I was really dejected. I had a really tough time, but I'm glad I was able to bounce back."

Parikh credited his success to a trio of coaches, relentless self-study using custom word lists and typing programs, and year-round competition in online spelling bees outside the Scripps circuit. He also took a deliberate six-month hiatus from spelling after his 2025 loss, returning with what he described as a renewed focus.

## The diaspora's quiet dominance

The 2026 bee brought 247 contestants from across all 50 U.S. states, the District of Columbia, Guam, Puerto Rico, the U.S. Virgin Islands, and several countries including Canada, Ghana, Nigeria, and the UAE. Of the nine finalists, five were of Indian origin — a ratio that, at this point, barely registers as news.

Indian-American spellers have won 21 of the last 28 Scripps titles. The streak stretches back to 2008 and has survived only two interruptions: Zaila Avant-garde's historic victory in 2021 and Faizan Zaki's win in 2025. Sarv Dharavane, 12, of Tucker, Georgia — also of Indian origin — placed third for the second consecutive year. Kushi Gottimukkala finished fourth.

The dominance has drawn its share of commentary, some admiring and some reductive. What it reflects, more than anything, is infrastructure. Indian-American families have built an entire ecosystem around competitive spelling: coaching networks, year-round practice circuits, study groups, and word analysis communities that operate largely outside the Scripps apparatus. Parikh himself told reporters that "spelling fast is what I do every day, so the spell-off kind of came naturally."

## More than a trophy

Beyond the $52,500 prize, the Scripps Cup, the Merriam-Webster gift, and the Delta flight credits, Parikh's win carries a specific resonance at a specific moment. Indian Americans constitute roughly 1.5 per cent of the U.S. population but account for an outsized share of high-achieving youth in academic competitions — from spelling to science fairs to math olympiads. That visibility has become a double-edged sword in an era of rising anti-Indian sentiment and political scapegoating.

For the diaspora, the Bee remains one of the most joyful annual markers of what a community built on education and perseverance can produce. It is not policy. It is not politics. It is a teenager standing alone under lights, spelling words most adults have never heard, with the calm of someone who has done this ten thousand times before.

Parikh is the first Californian to win since Ananya Vinay of Fresno took the title in 2017. He will enter high school this fall at Etiwanda's Day Creek Intermediate School. His other interests include tennis, chess, percussion (snare drum, timpani, marimba), and visiting his grandparents in India.

He plans to keep spelling."""
    },
    # ──────────────────────────────────────────────
    # Article 2: NY State Caste Bills fail
    # ──────────────────────────────────────────────
    {
        "id": str(uuid.uuid4()),
        "headline": "New York's Caste Bills Are Dead. The Hindu Community That Killed Them Wants to Talk About What Almost Happened.",
        "subheadline": "After two years of grassroots lobbying by the Coalition of Hindus of North America, Senate Bill S.6531 and Assembly Bill A.6920 failed to advance — a victory that Hindu advocacy groups say stopped a religiously coded ethnic classification from becoming law.",
        "slug": make_slug("new-york-caste-bills-dead-cohna-hindu-community-advocacy"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The bills would have added 'caste' as a protected category under New York's Human Rights Law — language that Hindu and Indian-American advocacy groups argued would single out their community for stereotyping and institutional bias. The outcome is the latest chapter in a legislative battle that has played out across California, Seattle, and now New York.",
        "tags": ["nri", "diaspora", "caste", "legislation", "hindu", "new-york", "civil-rights", "advocacy"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CoHNA Press Release via PR Newswire / WCIA", "url": "https://www.wcia.com/business/press-releases/cision/20260605CL77300/win-for-equality-as-new-york-state-caste-bills-targeting-american-hindus-fail-to-advance/"},
            {"name": "Rutgers Social Perception Lab / NCRI Study (2024)", "url": "https://www.ncri.io/"},
            {"name": "Carnegie Endowment — Indian Americans in a Time of Turbulence (2026)", "url": "https://carnegieendowment.org/preview/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"}
        ]),
        "score_total": 74,
        "status": "published",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/f/fc/New_York_State_Capitol_building%2C_full.jpg/1280px-New_York_State_Capitol_building%2C_full.jpg",
        "image_caption": "The New York State Capitol in Albany, where caste-related human rights legislation failed to advance",
        "image_attribution": "Wikimedia Commons",
        "is_editorial": False,
        "body": """Two bills that sought to add "caste" as a protected category under New York State's Human Rights Law will not become law this session. Senate Bill S.6531 and Assembly Bill A.6920, first introduced in 2025 and reintroduced in 2026, failed to advance through the legislature — an outcome that the Coalition of Hindus of North America (CoHNA) announced on June 5 as a "win for equality."

The collapse of the bills ends, for now, the latest front in a legislative battle that has ricocheted across the United States for half a decade. Seattle became the first U.S. city to ban caste discrimination in 2023. California's Civil Rights Department pursued a high-profile caste discrimination lawsuit against Cisco that was ultimately withdrawn "with prejudice" — a legal outcome that CoHNA says exposed the case as baseless. New York was the next proving ground.

## What the bills would have done

The proposed legislation would have inserted the word "caste" into New York's existing anti-discrimination framework, making it an explicit protected class alongside race, religion, gender, and national origin. Proponents, many of them academics and Dalit advocacy groups, argued the addition was necessary to address discrimination that existing categories fail to capture — particularly in workplaces with large South Asian populations.

Opponents saw something more dangerous. CoHNA and allied organizations argued that the bills lacked "facial neutrality" and would institutionalise a religiously coded ethnic classification that disproportionately targets Hindus and Indian Americans. Their core objection: existing anti-discrimination law already covers caste-based mistreatment without singling out a specific community.

"This was yet another attempt to misuse a noble desire for social justice and subvert it to drive hate against a minority, like we saw in California in 2023," said Nikunj Trivedi, CoHNA's president.

## Two years of hallway lobbying

CoHNA's campaign was deliberately grassroots. Over two years, the organisation held dozens of meetings with New York state legislators, including the bills' sponsors. Hundreds of community members sent emails to their assembly members and state senators. A legal memorandum outlining constitutional concerns was distributed to all 213 members of the New York State Assembly and Senate.

The most striking element was who led the opposition. CoHNA's Dalit Bahujan leadership team — members of the very communities that caste protections are ostensibly designed to help — spoke publicly against the bills.

"As a Bahujan Hindu myself, I have held many meetings with lawmakers in New York for the past two years to share my story and to educate," said Sudha Jagannathan, CoHNA's director of government relations. "I find it offensive that New York State would try to weaponize my identity against my own culture and traditions that provide me solace and strength."

## The science of stigma

The debate is no longer confined to legislative chambers and op-ed pages. A 2024 study from the Rutgers University Social Perception Lab and the Network Contagion Research Institute found that even casual references to caste by people in positions of institutional power produced measurable harm — including making individuals more likely to agree with anti-Hindu statements that researchers described as "Hitler-like."

The finding gave advocacy groups a new empirical weapon. If caste legislation primes bias rather than preventing it, the policy cure may be worse than the disease.

CoHNA also pointed to the Cisco case as a cautionary tale. California's Civil Rights Department assigned both a religion and a caste to Sundar Iyer, an atheist employee, based solely on his South Asian background. The case was withdrawn before trial, and the department narrowly avoided sanctions from a California court.

## The broader context

The New York fight unfolded against a backdrop of rising anti-Indian sentiment in the United States. The 2026 Carnegie Endowment survey of Indian Americans found that one in four respondents had been called a racial slur since the start of 2025. Nearly half reported encountering racist posts targeting Indians on social media "very or somewhat often." Nine per cent said they had been physically threatened.

For Hindu Americans, caste legislation adds a layer of institutional vulnerability to an already fraught environment. The concern is not that discrimination does not exist — it is that legislation designed to address it may instead codify the very stereotypes that fuel it.

"It is important to remember that caste is not a neutral word," Trivedi said. "Due to decades of misinformation, it is primarily associated with the Hindu and Indian communities in public perception. It is used by ideological rivals on the far-Right and ultra-Left alike to otherize and harm our community."

## What comes next

The failure of the New York bills does not settle the question. Caste-related legislation has been proposed in multiple jurisdictions, and advocacy on both sides shows no sign of slowing. For the Indian-American community, the debate touches on some of the most sensitive questions of diasporic identity: who speaks for whom, how colonial-era categories translate into American law, and whether the language of social justice can be turned into a weapon against the communities it purports to protect.

For now, in Albany, the answer was no."""
    },
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
