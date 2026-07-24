#!/usr/bin/env python3
"""NRI World Writer — 29 June 2026, 5 PM PT run."""

import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# ── Supabase env ────────────────────────────────────────────────────
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


# ════════════════════════════════════════════════════════════════════
# ARTICLE 1 — AIF Record Gala
# ════════════════════════════════════════════════════════════════════

art1_body = """Six hundred guests filled Cipriani Wall Street on June 9 for the American India Foundation's silver-jubilee gala. By the end of the night, they had pledged a record $3.8 million — roughly the cost of educating 15,000 children in rural India for a year through AIF's programmes. Over $1 million of that came from a single pledge drive, led by Global Board member Saira Lal's $300,000 commitment.

The evening honoured three pillars of the Indian-American corporate landscape. BNY, one of the oldest banks in the United States, received the corporate citizenship award. Bharat Masrani, the recently retired CEO of TD Bank Group, was recognised for his decades-long advocacy of immigrant-powered enterprise. And Salil Parekh, the CEO and Managing Director of Infosys, was lauded for steering the IT giant's growing investment in American workforce training.

"We all had someone in our lives who believed in us," Masrani told the crowd. "Someone who looked at us and saw — not what we were at that moment, but what we could become. AIF's mission makes this possible for millions." Parekh struck a more forward-looking note, tying technology to equity: "As we navigate an AI-first era, our shared responsibility is to ensure that technology expands human potential."

The three honorees together represent a diaspora corridor that now runs from Mumbai's software campuses through Bay Street in Toronto to the trading floors of Lower Manhattan. That corridor, AIF argues, is where philanthropic dollars can have the most leverage. Since 2001, the foundation has channelled diaspora money into public health, education and livelihood programmes across 35 Indian states and union territories, reaching more than 23 million lives.

The gala comes at an inflection point for Indian-American giving. A landmark Dalberg-Indiaspora study published last October found that diaspora giving had nearly tripled to an estimated $4–5 billion in 2024, shrinking the "giving gap" — the difference between actual donations and giving potential — from $2–3 billion to just $1 billion. Higher-income Indian Americans now donate a larger share of income than the U.S. average, the study found.

That shift is partly structural. Sixteen Indian-origin CEOs head Fortune 500 companies, collectively employing 2.7 million Americans and generating nearly $1 trillion in revenue. Indians have co-founded 72 of the 648 American unicorns operating as of 2024. Wealth is accumulating in the community faster than established giving networks can channel it.

AIF is trying to fill that gap. Its Learning and Migration Programme, or LAMP, tracks seasonal migrant children across India's brick kilns and sugarcane fields, enrolling them in bridge schools so they don't fall permanently behind. The programme won an award from the United Nations and was showcased at the gala through a virtual-reality experience designed to bring donors face-to-face with the children they fund.

The gala's presenting sponsors — BNY, Goldman Sachs Gives and TD Bank — signal corporate America's growing comfort with diaspora-led philanthropy as a legitimate channel for impact investing. "AIF at 25 shows that enduring impact is possible when people come together across borders," said CEO Nishant Pandey. "I cannot be more excited about the next 25 years."

For the diaspora, the subtext is plain. Indian Americans now pay an estimated five to six per cent of all U.S. income taxes, claim roughly 11 per cent of NIH grants and contribute to 13 per cent of scientific publications. The community's civic footprint has outgrown the fundraiser circuit. AIF's silver jubilee is less a celebration than a challenge: the infrastructure for giving exists, the money exists, and — as the gala's VR booth made viscerally clear — so does the need."""

art1 = {
    "id": str(uuid.uuid4()),
    "headline": "The Diaspora's Philanthropy Machine Just Turned 25. It Raised a Record $3.8 Million in One Night.",
    "subheadline": "The American India Foundation's silver-jubilee gala honoured BNY, Bharat Masrani and Salil Parekh — and marked a turning point for Indian-American giving that has nearly tripled in six years.",
    "slug": make_slug("aif-gala-record-38-million-diaspora-philanthropy-25-years"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian-American philanthropy has reached an inflection point, with giving tripling to $4–5 billion and the gap between potential and actual donations shrinking to $1 billion. AIF's gala channels that energy into education, health and livelihoods across India.",
    "tags": ["nri", "diaspora", "philanthropy", "aif", "indian-american"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "PR Newswire / American India Foundation", "url": "https://www.prnewswire.com/news-releases/american-india-foundation-raises-record-3-8-million-at-annual-new-york-gala-celebrating-25-years-of-impact-302798121.html"},
        {"name": "Dalberg / Indiaspora Philanthropy Report", "url": "https://dalberg.com/our-ideas/indian-american-philanthropy-narrows-giving-gap/"},
        {"name": "The Indian Eye — Indian Americans' Contributions Report", "url": "https://theindianeye.com/2025/12/19/small-community-big-contributions-as-indian-americans-pay-about-5-6of-all-income-taxes-in-the-us/"},
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/98/Bharat_masrani_td_bank_by_bill_cramer_1.jpg",
    "image_caption": "Bharat Masrani, retired CEO of TD Bank Group, was honoured at AIF's 25th-anniversary gala at Cipriani Wall Street",
    "image_attribution": "Wikimedia Commons",
    "body": art1_body.strip(),
}

# ════════════════════════════════════════════════════════════════════
# ARTICLE 2 — Belfast Riots & Indian Community
# ════════════════════════════════════════════════════════════════════

art2_body = """When masked men went door-to-door in parts of Belfast on the night of June 9, checking who lived where and setting fire to houses believed to shelter immigrants, Ruchira Rangaprasad knew she could not just watch from her phone screen. The Indian-born Northern Ireland resident posted on social media that she would cook meals for displaced families. By the next morning, more than 30 strangers — most of them white and Northern Irish — had volunteered to help her distribute food boxes across the city.

Her story became one of the quiet counter-narratives to three days of anti-immigration violence that shook Belfast and rippled into other parts of Northern Ireland, as well as Glasgow, Edinburgh and Southampton. The riots, triggered by a stabbing attack for which a Sudanese man was charged with attempted murder, saw homes and vehicles torched, shops attacked and what *The Times* called "spontaneous pogroms." Police deployed water cannon and plastic bullets; 27 people were made homeless.

The violence did not target Indians specifically. But the fear it seeded ran through every minority community in the city. Union volunteers evacuated at least 30 families over two nights. Healthcare workers reported being stopped by vigilante patrols near hospitals, their ethnicity questioned and their car registrations filmed. A nurse was chased by four masked men outside a hospital in east Belfast. "This is hatred that is putting lives at risk," said Patricia McKeown, regional secretary of the public-sector union Unison.

For the roughly 40,000 people of Indian origin in Northern Ireland and the broader UK, the Belfast riots land at a moment of compounding unease. INSIGHT UK, a Hindu community safety organisation, issued detailed guidance urging families to install CCTV cameras, use well-lit travel routes and report hate crimes through the police and the Stop Hate UK hotline. The advisory carried the weight of experience: Britain has seen rolling anti-immigration protests since 2025, some organised by far-right groups, with tensions intensifying after a series of violent crimes amplified on social media.

Northern Ireland is 97 per cent white, according to its 2021 census. Its three decades of sectarian conflict between Catholic nationalists and Protestant loyalists have been, in recent years, partly supplanted by hostility toward ethnic minorities, community organisers say. The pattern is familiar across Europe: economic stagnation and housing pressure channelled into nativist anger, accelerated by social-media algorithms that reward outrage over context.

What distinguished the Belfast aftermath was the speed and scale of the community response. On June 13, large crowds gathered in Belfast and Derry for counter-protests, carrying banners reading "Riots don't speak for Belfast" and "Belfast stands against racism." Kashif Akram, a member of the executive committee at the Belfast Islamic Centre, said the rally showed the city's truer face. "The people who are spreading the hate at the moment, they are a minority," he told Reuters. "There are very few."

For Indians in the UK, the episode underscores a tension that runs beneath the community's outward success. Indian Britons are disproportionately represented in medicine, technology and small business — exactly the professionals that keep a post-conflict city like Belfast running. When a nurse is chased through a hospital car park for looking foreign, the city is attacking its own immune system.

Rangaprasad's food boxes are a small act, easily romanticised. But they point to something the diaspora understands instinctively: in a crisis, the community feeds itself before it waits for institutions to catch up. The question for Indian residents in Northern Ireland, as the summer protest season continues, is whether the institutions will catch up at all."""

art2 = {
    "id": str(uuid.uuid4()),
    "headline": "Belfast Burned. An Indian Woman Fed the Families Left Behind.",
    "subheadline": "Anti-immigration riots in Northern Ireland displaced dozens of minority families. For the Indian community in the UK, the violence has deepened a quiet unease about safety that no advisory can fully address.",
    "slug": make_slug("belfast-riots-indian-community-uk-safety-rangaprasad"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The Belfast riots forced Indians and other ethnic minorities in Northern Ireland to confront their vulnerability. Ruchira Rangaprasad's community meal drive and INSIGHT UK's safety advisory for Hindu communities reflect a diaspora learning to protect itself in an increasingly hostile European landscape.",
    "tags": ["nri", "diaspora", "uk", "belfast", "community-safety", "hate-crime"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/uk/belfasts-minority-groups-living-fear-after-racist-thuggery-2026-06-11/"},
        {"name": "Wikipedia — 2026 Northern Ireland riots", "url": "https://en.wikipedia.org/wiki/2026_Northern_Ireland_riots"},
        {"name": "INSIGHT UK — Safety Guidance for Hindu and Indian Communities", "url": "https://insightuk.org/safety-guidance-for-hindu-and-indian-communities-in-the-uk/"},
        {"name": "Reuters — UK minister calls violence 'racist thuggery'", "url": "https://www.reuters.com/world/uk/uk-minister-says-violence-northern-ireland-is-racist-thuggery-2026-06-11/"},
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/City_Hall%2C_Donegall_Square%2C_Belfast_%287560740480%29.jpg/1280px-City_Hall%2C_Donegall_Square%2C_Belfast_%287560740480%29.jpg",
    "image_caption": "Belfast City Hall — the heart of a city that erupted in anti-immigration violence in June 2026",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}


# ── Insert ──────────────────────────────────────────────────────────
articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
