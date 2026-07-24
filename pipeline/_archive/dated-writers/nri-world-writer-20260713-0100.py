#!/usr/bin/env python3
"""NRI World writer – July 13 2026, 01:00 PT run."""

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
    r = requests.post(
        f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30
    )
    r.raise_for_status()
    return r.json()


now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def make_slug(base):
    slug = base.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    return slug[:70].rstrip("-") + "-" + datetime.now().strftime("%Y%m%d")


# ── Article 1: Indian-Origin Mayors ──────────────────────────────────────

art1_body = """\
When Raj Salwan was sworn in as mayor of Fremont, California last December, the ceremony carried a significance that extended well beyond a single East Bay city. Salwan, born in a village near Amritsar, Punjab, and brought to the United States at the age of six, had become the first Indian American to lead a city of nearly 230,000 people in one of the most diverse corridors of the San Francisco Bay Area. Three weeks later, on January 3, 2026, Pulkit Desai — a US Marine combat veteran born in India — took the oath of office as mayor of Parsippany-Troy Hills, New Jersey, becoming the first Indian American and first Asian American to lead Morris County's largest municipality.

The two swearing-in ceremonies, separated by a continent and three thousand miles, were not coincidences. They were data points in a pattern that Indian American civic organisations have tracked with growing confidence: the community's movement from boardrooms and operating theatres into the corridors of local government.

## From Veterinarian to City Hall

Salwan's path to the Fremont mayoralty followed two decades of incremental civic engagement. After earning a degree in biological sciences from UC Irvine and a Doctor of Veterinary Medicine from Tuskegee University, he returned to Fremont — the city where he had attended elementary and high school in the 1980s — and began volunteering. Bob Wasserman, then the city's mayor, encouraged him to join the Human Relations Commission, which he did in 2005. A stint on the planning commission followed. In 2014, Salwan ran for city council and lost. He ran again in 2016 and won.

Over eight years on the council, Salwan built a record that included a thirty-three per cent reduction in traffic congestion and a committee to allocate land for school construction — the kind of granular, infrastructure-focused work that rarely makes national headlines but directly shapes residents' daily lives. When former mayor Lily Mei was termed out, Salwan won the 2024 election and assumed office in December.

"People want someone who understands the day-to-day challenges of running a city," Salwan told CBS News after his victory. Fremont, home to Tesla's main factory and a growing tech workforce, has become a bellwether for how rapidly diversifying American cities govern themselves.

## Eighty Votes in New Jersey

If Salwan's election was a relatively comfortable culmination of years of groundwork, Pulkit Desai's victory was a white-knuckle affair. On election night in November 2025, Republican incumbent James Barberio led by 211 votes. It was only when provisional and mail-in ballots were counted on November 12 that Desai pulled ahead — by a margin of eighty votes out of nearly 20,000 cast, or roughly 50.05 per cent to 49.65 per cent.

Barberio filed three separate legal challenges to the result. All failed. On January 3, 2026, with New Jersey Governor-elect Mikie Sherrill in attendance, Desai was sworn in by State Senator Raj Mukherji.

Desai's biography alone tells a distinctly American story. Born in India, he enlisted in the US Marine Corps and was activated during Operation Desert Shield and Desert Storm, where he led Marines in mission-critical operations and earned the Navy Achievement Medal. He later moved into technology, eventually settling in Parsippany's Lake Parsippany neighbourhood. He served as president of the Lake Parsippany Property Owners Association, one of New Jersey's largest common-interest communities, where he restored voting rights and tightened financial oversight for more than 2,200 property owners.

"The most important thing is transparency and accountability," Desai said in his first interview after taking office. "No backroom deals. Nothing hidden."

## A Broader Pattern

Salwan and Desai are not isolated cases. Indian Americans have been winning local offices at an accelerating pace. Aftab Pureval has served as mayor of Cincinnati since 2022. In Los Angeles, Nithya Raman — a Chennai-born urban planner — is running in a competitive mayoral race after flipping a city council seat in 2020. At the township and council level, Indian Americans now hold seats in dozens of municipalities across New Jersey, Texas, Georgia, and Virginia, reflecting a community whose median household income and educational attainment — the highest of any ethnic group in the United States, according to the Census Bureau — has begun translating into political capital.

The shift is partly demographic. Parsippany-Troy Hills, once overwhelmingly white, now counts Asian Americans as its largest ethnic group. Fremont's Indian American population is among the largest in California. But demography alone does not explain politics. Both Salwan and Desai ran on platforms of competence and local governance — traffic, schools, infrastructure, fiscal discipline — rather than identity. Their campaigns suggest that Indian American candidates are winning not because they are Indian American, but because they have done the unglamorous work of civic engagement that precedes any election.

For a diaspora community that has long excelled in private-sector leadership — Satya Nadella, Sundar Pichai, Arvind Krishna — the movement into public office represents a different kind of ambition: not to build wealth, but to shape the communities where their families live.
"""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "From Fremont to Parsippany: Indian-Origin Mayors Are Making History Across America",
    "subheadline": "Raj Salwan and Pulkit Desai lead a growing wave of Indian Americans winning local elections, reflecting the community's deepening civic roots.",
    "slug": make_slug("indian-origin-mayors-fremont-parsippany-history-america"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian Americans are translating decades of private-sector success into local political leadership, with first-generation immigrants winning mayoral races in diverse cities from California to New Jersey.",
    "tags": ["nri", "diaspora", "politics", "mayors", "indian-american", "civic-engagement", "fremont", "parsippany"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Wikipedia – Raj Salwan", "url": "https://en.wikipedia.org/wiki/Raj_Salwan"},
        {"name": "American Kahani", "url": "https://americankahani.com/politics/marine-combat-veteran-pulkit-desai-sworn-in-as-mayor-of-parsippany/"},
        {"name": "CBS News", "url": "https://www.cbsnews.com/sanfrancisco/news/fremonts-first-indian-american-mayor-has-big-plans-for-east-bay-city/"},
        {"name": "Samba English", "url": "https://sambadenglish.com/indian-american-pulkit-desai-sworn-in-as-new-jersey-city-mayor/"},
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6f/Raj_Salwan.jpg",
    "image_caption": "Raj Salwan, the first Indian American mayor of Fremont, California",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}


# ── Article 2: Dr. Dileep Yavagal Lifetime Achievement Award ─────────────

art2_body = """\
At the 2026 American Academy of Neurology Annual Meeting, the Association of Indian American Neurologists — in collaboration with the American Brain Foundation — presented Dr. Dileep R. Yavagal with a Lifetime Achievement Award, honouring a career that has fundamentally altered how strokes are treated from Miami to Mumbai and in more than ninety countries in between.

The award recognises Yavagal's central role in establishing mechanical thrombectomy — the physical extraction of blood clots from the brain — as the standard of care for acute ischemic stroke, the type responsible for roughly eighty-seven per cent of all stroke cases worldwide. It is a story that begins in India, passes through three of America's most prestigious medical schools, and arrives at a global health initiative that has quietly become one of the most consequential in modern neurology.

## From India to Harvard to Miami

Yavagal was born and completed his early medical training in India before moving to the United States for advanced fellowships at Harvard, Columbia, and UCLA — an academic lineage that placed him at the intersection of clinical practice and research. He eventually settled at the University of Miami, where he now serves as chief of Interventional Neurology and co-director of Neuroendovascular Surgery at Jackson Memorial Hospital, one of America's largest public hospitals.

It was at Miami that Yavagal's research took on its defining character. His contributions to the SWIFT PRIME trial — one of a handful of landmark studies conducted in the mid-2010s — helped establish that mechanical thrombectomy, performed within hours of stroke onset, dramatically improved outcomes compared with medication alone. The trial's results were so decisive that they prompted the American Heart Association and stroke authorities worldwide to rewrite their treatment guidelines. Thrombectomy went from an experimental procedure to the global standard virtually overnight.

## Mission Thrombectomy: A Global Initiative

If the SWIFT PRIME trial proved the science, Yavagal's next project addressed the harder question: who actually benefits from it?

The answer, he discovered, was troublingly unequal. His research exposed critical gaps in stroke care within the United States itself, demonstrating that rural patients were far less likely to receive thrombectomy than their urban counterparts — even when they presented within the treatment window. The disparity was worse in lower-income countries, where many hospitals lacked the equipment, training, or awareness to perform the procedure at all.

In response, Yavagal founded Mission Thrombectomy, a global initiative that has since expanded to more than ninety countries. The programme trains physicians, builds local capacity, and works to ensure that the life-saving procedure is not confined to wealthy urban medical centres. It is, in effect, an effort to close the gap between what medicine can do and what most patients actually receive.

The initiative's reach is particularly significant in South Asia, sub-Saharan Africa, and Latin America, where stroke burden is high but interventional neurology infrastructure remains limited. In India, where stroke is the fourth-leading cause of death, Mission Thrombectomy has partnered with hospitals to establish thrombectomy-capable centres in cities that previously had none.

## Mentoring the Next Generation

Beyond his clinical and research contributions, Yavagal has mentored dozens of neurologists who now lead stroke programmes at institutions across the world. Several of his former trainees head interventional neurology departments at major academic medical centres in the United States, Europe, and Asia — extending the influence of his training far beyond Miami.

The Lifetime Achievement Award from the Association of Indian American Neurologists carries a particular resonance. Indian-origin physicians constitute one of the largest cohorts in American medicine — the American Association of Physicians of Indian Origin estimates more than 100,000 members — yet recognition at this level, for work that has reshaped an entire field of treatment, remains rare.

## The Diaspora's Medical Footprint

Yavagal's career illustrates a pattern that runs through the Indian medical diaspora. Physicians trained in India's highly competitive medical schools arrive in the United States, complete further training at elite institutions, and then produce work that flows back to the countries their families left. The knowledge transfer is not one-directional; it is a circuit. Mission Thrombectomy is, in a sense, the institutional expression of that circuit — taking research developed in American academic medicine and making it operational in the hospitals where it is most desperately needed.

For the global stroke community, the award is an acknowledgement that the field's progress over the past two decades — from a condition that was largely managed with medication and hope to one that can be treated with precise, evidence-based intervention — owes a significant debt to the work of an Indian-born neurologist working out of a public hospital in South Florida.
"""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Indian American Neurologist Wins Lifetime Achievement Award for Transforming Global Stroke Care",
    "subheadline": "Dr. Dileep Yavagal, founder of Mission Thrombectomy active in over ninety countries, honoured for reshaping how the world treats the leading cause of disability.",
    "slug": make_slug("dileep-yavagal-lifetime-achievement-stroke-care"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Yavagal's career traces the circuit of the Indian medical diaspora — training in India, research breakthroughs at American institutions, and a global initiative that channels those advances back to underserved communities worldwide, including in South Asia.",
    "tags": ["nri", "diaspora", "medicine", "neurology", "stroke", "achievement", "healthcare", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "ePadosi", "url": "https://www.epadosi.com/news/indian-american-neurologist-dileep-yavagal-wins-top-honor-for-transforming-stroke-care-xtmv9kx2ui"},
        {"name": "University of Miami Health System", "url": "https://med.miami.edu"},
        {"name": "Mission Thrombectomy", "url": "https://missionthrombectomy.org"},
    ]),
    "score_total": 73,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/4226139/pexels-photo-4226139.jpeg?auto=compress&cs=tinysrgb&w=1200",
    "image_caption": "A medical professional examines a brain MRI scan in a neurology clinic",
    "image_attribution": "Pexels/Anna Shvets",
    "body": art2_body.strip(),
}


# ── Insert ────────────────────────────────────────────────────────────────

for label, art in [("1 (Mayors)", art1), ("2 (Yavagal)", art2)]:
    try:
        resp = sb_post("p2_articles", art)
        title = resp[0]["headline"] if resp else art["headline"]
        print(f"✅ Article {label} inserted: {title}")
        print(f"   slug: {art['slug']}")
    except Exception as exc:
        print(f"❌ Article {label} FAILED: {exc}")

print("\nDone.")
