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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "India Sent 112 Companies to Canada in Its Largest-Ever Trade Delegation. The Diaspora Built the Landing Strip.",
        "subheadline": "Piyush Goyal's three-day blitz through Toronto and Ottawa produced a new trade forum, a Canadian counter-mission to India, and a shared ambition to triple bilateral trade to $50 billion by 2030. The 1.9 million Indo-Canadians who made it all possible were sitting in the front row.",
        "slug": make_slug("india-largest-trade-delegation-canada-cepa-goyal-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The Indo-Canadian diaspora — 1.9 million strong and growing — served as the connective tissue for the largest Indian business delegation ever sent abroad. The visit explicitly credited the community with bringing the two nations closer through business engagement and people-to-people ties, while CEPA negotiations that could reshape NRI trade corridors inch toward a year-end deadline.",
        "tags": ["nri", "diaspora", "india-canada", "cepa", "trade", "piyush-goyal"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/piyush-goyal-lauds-role-of-indian-diaspora-in-canada/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/india-and-canada-aim-for-usd-50-billion-trade-by-2030/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/canada-announces-trade-mission-to-india/"},
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/28/india-and-canada-launch-trade-and-investment-forum/"}
        ]),
        "score_total": 78,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/63/Piyush_Goyal_crop.jpg",
        "image_caption": "Union Commerce Minister Piyush Goyal, who led India's largest-ever business delegation to Canada",
        "image_attribution": "Wikimedia Commons",
        "body": """When Piyush Goyal landed in Toronto on May 25, he brought luggage that no Indian commerce minister had carried before: 112 companies, spanning metals, energy, aerospace, pharmaceuticals, textiles, and telecom. It was, by the ministry's own accounting, the largest business delegation India has ever dispatched to a single country. Three days, two cities, and a flurry of memoranda later, the trip left behind something more durable than photo opportunities — a new institutional architecture for a trade relationship that both sides want to multiply sixfold in four years.

## The Numbers and the Gap

Bilateral trade between India and Canada currently stands at roughly $8.5 billion annually. Both governments have now committed, publicly and repeatedly, to reaching $50 billion by 2030. That target sounds aspirational until you consider the trajectory: Prime Minister Mark Carney's visit to India earlier this year set the tone, and Goyal's delegation was designed to convert diplomatic warmth into deal flow.

The centrepiece was the launch of the Canada-India Trade and Investment Forum, a standing platform to bring CEOs, institutional investors, and industry associations from both countries into regular contact. At a fireside chat in Toronto with Canadian Trade Minister Maninder Sidhu, Goyal described the forum as a mechanism for "a more robust and predictable business ecosystem driven by stronger government-industry collaboration."

Sidhu, for his part, announced a Team Canada Trade Mission to India in November — a reciprocal delegation targeting AI, critical minerals, nuclear energy, semiconductors, and advanced manufacturing. The move signals that the courtship is no longer one-directional.

## CEPA: The Deal That Could Change Everything

Behind the press conferences, the real prize is the Comprehensive Economic Partnership Agreement, or CEPA — a free-trade pact that has been under negotiation for years but now carries a year-end deadline. Goyal and Sidhu co-chaired an investment roundtable and provided what the ministry called "clear guidance" to negotiating teams to deliver "a balanced, commercially meaningful and ambitious agreement."

If CEPA lands, it would be transformative for NRIs with business interests straddling both countries. Reduced tariffs, simplified rules of origin, and mutual recognition frameworks would lower the friction that currently makes cross-border ventures in sectors like food processing, clean energy, and digital infrastructure more expensive than they need to be.

Goyal's meetings with Ontario Premier Doug Ford covered manufacturing, clean technology, infrastructure, and critical minerals — sectors where Canada's resource abundance and India's manufacturing scale are natural complements. Separate meetings with the Ontario Teachers' Pension Plan and CPP Investments explored infrastructure, renewables, logistics, and the digital economy. These are not speculative conversations; they are the kind of institutional capital deployment that follows political alignment.

## The Diaspora as Infrastructure

What made the delegation unusual was not just its size but its framing. Goyal explicitly credited the Indo-Canadian community — estimated at 1.9 million and growing, according to Canada's 2026 census — with "bringing the two nations closer through stronger business engagement and people-to-people ties." He met with the Canada-India Foundation, an organisation that has spent decades cultivating exactly these corridors.

This is not merely rhetorical. The Indo-Canadian diaspora is concentrated in sectors — technology, finance, healthcare, real estate — that map neatly onto the CEPA negotiation agenda. Many hold dual professional networks, one foot in Toronto or Vancouver and the other in Bengaluru or Mumbai. When Goyal says the trade target is "very much doable," it is partly because the human infrastructure already exists.

The delegation also engaged with the University of Toronto's Munk School of Global Affairs and the Ontario Centre of Innovation, with discussions covering AI, quantum computing, and clean technology — areas where Indian talent and Canadian research ecosystems have obvious synergies.

## What Comes Next

The November trade mission will be the next visible marker. If CEPA negotiations stay on schedule, the deal could be signed before year-end — a timeline both ministers affirmed publicly. For the diaspora, the practical implications are significant: easier movement of goods, capital, and people across a corridor that already carries $8.5 billion in annual commerce.

For the 1.9 million Indo-Canadians watching from the front row, the message from both governments was unusually direct: you are not just beneficiaries of this relationship. You built it."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A State Senator, a Biotech Pioneer, and a Banker Who Came From Mumbai. Connecticut Just Honoured Five Indian Americans Who Built Careers Across Continents.",
        "subheadline": "GOPIO-Connecticut's 20th anniversary gala on June 13 will recognise achievers in politics, antiviral research, journalism, banking, and engineering — each of them a case study in what the diaspora looks like when it puts down roots.",
        "slug": make_slug("gopio-ct-20th-anniversary-five-indian-american-honorees"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Each of the five honourees represents a different facet of the Indian American experience in New England: a Fulbright scholar who became a state senator, a biotech founder whose antiviral technology is in clinical trials in Africa, a journalist who also practices clinical social work at Yale, a banker who rose from Mumbai University to lead a 174-year-old community bank, and an IIT Kharagpur graduate with 10 US patents. Together, they illustrate how deeply the diaspora has woven itself into Connecticut's institutional fabric.",
        "tags": ["nri", "diaspora", "gopio", "connecticut", "indian-american", "awards"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/2026/05/29/gopio-ct-to-honor-five-indian-american-achievers-at-its-20th-anniversary/"},
            {"name": "GOPIO International", "url": "https://www.gopio.net/"}
        ]),
        "score_total": 65,
        "status": "published",
        "published_at": now,
        "is_editorial": False,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/f/f5/SujataGadkarWilcox.png",
        "image_caption": "Connecticut State Senator Sujata Gadkar-Wilcox, one of five Indian Americans being honoured at GOPIO-CT's 20th anniversary gala",
        "image_attribution": "Wikimedia Commons",
        "body": """The Global Organization of People of Indian Origin has chapters in cities across the world, but the Connecticut chapter holds a particular distinction: it has been running continuously for two decades in a state where the Indian American population is modest compared with New Jersey or California. On June 13, GOPIO-CT will celebrate that milestone with an awards banquet at the Water's Edge Banquet Hall in Darien, honouring five Indian Americans whose careers span politics, biotech, journalism, banking, and engineering. Several Connecticut lawmakers are expected to attend.

The honourees were chosen, as GOPIO-CT President Mahesh Jhangiani put it, because they "have made an impact in our society and/or those who provide outstanding service." What makes the list interesting is not just the individual achievements but the collective portrait it paints of a diaspora community that has embedded itself deeply in a state better known for hedge funds and colonial history.

## The Politician

Senator Sujata Gadkar-Wilcox has represented Connecticut's 22nd District since 2024, making her one of a small but growing cohort of Indian American state legislators outside the traditional coastal hubs. Before entering politics, she was a professor of Legal Studies at Quinnipiac University and a Fulbright-Nehru Scholar who spent two years in India researching constitutional values and democratic institutions. Her academic work spans constitutional law, human rights, media studies, and civic education — a combination that reads like a syllabus for the diaspora experience itself.

## The Biotech Pioneer

Dr. Anil Diwan founded NanoViricides, Inc. (NYSE American: NNVC), where he developed a class of antiviral drugs called "nanoviricides" — engineered molecules designed to target and destroy viruses. The company's lead candidate, NV-387, is a broad-spectrum antiviral currently in Phase II clinical trials for mpox in the Democratic Republic of Congo, with development also advancing for potential use against Ebola outbreaks in Africa. The technology has shown activity in company studies against coronaviruses, influenza, RSV, measles, and smallpox — a portfolio that reflects both scientific ambition and a willingness to tackle diseases that disproportionately affect the developing world.

## The Journalist

Ajay Ghosh carries two professional identities that rarely overlap: he is a veteran journalist with more than three decades of experience — publisher of The Global Net News and Health and Wellness News, former editor at The Indian Express (North America), and founder of the Indo-American Press Club — and simultaneously a Licensed Clinical Social Worker at Yale New Haven Hospital. He also teaches at Fordham's Graduate School. The dual career in media and healthcare speaks to a pattern common in the diaspora: the refusal to be defined by a single category, and the insistence on community-facing work alongside professional achievement.

## The Banker

Nitin Mhatre became CEO of First County Bank on April 15, 2026, taking the helm of a community bank that has served Fairfield County for more than 174 years. His path to that corner office began at Mumbai University, where he earned engineering and MBA degrees before moving to the United States. He subsequently held senior leadership roles at Webster Bank and Citibank, chaired the Consumer Bankers Association during 2019-2020, and completed executive education at Harvard Business School. In a state with no shortage of financial talent, Mhatre's appointment to lead one of its oldest community banks is a quiet marker of how far the diaspora has come in American institutional life.

## The Engineer

Professor Hemchandra Shertukde has spent nearly four decades at the University of Hartford's College of Engineering, Technology, and Architecture. An IIT Kharagpur graduate with a PhD from the University of Connecticut, he is the author of 13 solo books, co-author of more than 40 technical books, has published over 100 research papers, holds 10 US patents, and has founded several technology and medical device companies in Connecticut and Florida. His career is a reminder that the Indian engineering diaspora is not confined to Silicon Valley; it extends to university labs and small-company entrepreneurship across the American northeast.

## A Community That Stayed

GOPIO International's founder-president, Dr. Thomas Abraham — himself one of GOPIO-CT's founding members — said the honourees are "role models for our new generations" who have helped build "a good image of India and Indian Americans in Connecticut." The chapter will also recognise its founding members and past presidents at the June 13 event, a gesture that acknowledges the quiet, unglamorous work of community organisation.

What the five profiles share, beyond individual distinction, is longevity. These are not people who passed through Connecticut on the way to somewhere else. They stayed, built practices and companies, ran for office, mentored students, and became part of the state's institutional fabric. For a diaspora community that is often discussed in terms of mobility and ambition, that rootedness is its own kind of achievement."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
