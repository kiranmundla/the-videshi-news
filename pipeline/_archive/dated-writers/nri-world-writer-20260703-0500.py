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
        "headline": "The USISPF Summit Honoured Three Business Titans. Sunil Mittal Used His Speech to Talk About Five Million Indians Instead.",
        "subheadline": "At the IX USISPF Leadership Summit in Washington, Bharti's chairman and India's ambassador to the US laid out a vision in which the diaspora is not a footnote to the India-US partnership but the load-bearing wall.",
        "slug": make_slug("usispf-summit-mittal-diaspora-bridge-kwatra-30-trillion"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Mittal explicitly framed the 5-million-strong Indian American community as the strategic bridge between India and the US — in trade, defence, and high technology. Ambassador Kwatra's $30 trillion roadmap positions the diaspora as investors, knowledge partners, and connectors in India's climb to developed-nation status by 2047.",
        "tags": ["nri", "diaspora", "usispf", "india-us-trade", "sunil-mittal", "vinay-kwatra"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/07/01/sunil-bharti-mittal-honored-with-2026-leadership-award-at-usispf-summit/"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/07/01/kwatra-outlines-indias-rise-to-30-trillion-economy-at-usispf-summit/"},
            {"name": "The Indian EYE", "url": "https://theindianeye.com/2026/06/27/india-us-trade-deal-hinges-on-tariff-gap-with-pakistan-usispf-chief/"},
            {"name": "LiveMint", "url": "https://www.livemint.com/"}
        ]),
        "score_total": 80,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/49/Sunil_Mittal.jpg",
        "image_caption": "Sunil Bharti Mittal, founder and chairman of Bharti Enterprises",
        "image_attribution": "Wikimedia Commons",
        "body": """When the US-India Strategic Partnership Forum handed Sunil Bharti Mittal its 2026 Leadership Award at the IX Leadership Summit in Washington this week, the Bharti Enterprises chairman did what you might not expect from a telecom mogul collecting a trophy: he pivoted away from himself.

"Indian diaspora of nearly five million people, largest anywhere in the world, has a beautiful bridge between India and US, helping the strategic relationship develop between the two nations, be that trade, defence, or indeed higher technologies," Mittal told the room, which included US Commerce Secretary Howard Lutnick and some of the most powerful corporate executives on both sides of the Pacific.

It was a line that cut through the usual summit boilerplate, and it carried weight coming from a man who built India's largest mobile network and now sits at the intersection of Indian enterprise and global capital. The USISPF honoured two other leaders alongside Mittal — V. Prem Watsa, chairman of Canada's Fairfax Financial, and Christopher T. Calio, CEO of defence giant RTX Corporation — all three recognised for strengthening the India-US economic corridor.

## The $30 trillion speech

But the most bracing remarks of the summit came from India's Ambassador to the United States, Vinay Mohan Kwatra, who laid out a macroeconomic trajectory so ambitious it would have sounded like fantasy a decade ago.

India's current GDP stands at roughly $4.3 trillion. Kwatra mapped a structured path: $7 trillion by the end of this decade, $14 trillion by the mid-2030s, and $25 to $30 trillion by 2047 — the centenary of Indian independence.

"A set of these three — our focus on economic growth, the global disruptions that throw both opportunities and challenges, and the hugely transformative measures at home — allows India actually to be a huge enabler internationally," Kwatra said. "Underwritten by the strength of our democracy, it makes us a builder of strong, trusted and reliable global partnerships in a manner that is unparalleled."

For the Indian diaspora, particularly the estimated 4.8 million Indian Americans who form the wealthiest and most educated immigrant community in the United States, this trajectory is not abstract. It shapes everything from remittance flows and venture investment in Indian startups to career calculations about whether to stay, return, or shuttle between both countries.

## The trade deal that won't land

Mittal also used his platform to nudge the stalled India-US trade deal forward, directly addressing Commerce Secretary Lutnick: "I'm hoping, Secretary Lutnick, that if not in days, but in a few weeks, India and the US will have a trade deal that we in the industry have been looking forward to."

The deal has been stuck on a problem that has nothing to do with spreadsheets, according to USISPF President Mukesh Aghi. India's tariff rate currently sits at 12.5 per cent; Pakistan's is 10 per cent. "No political leader in India will accept that," Aghi said bluntly, "because it would essentially cost them elections."

For NRI-owned businesses and diaspora entrepreneurs who operate across both markets, this gap is not a statistical curiosity. It directly affects cost structures, competitive positioning, and the practical viability of cross-border operations — from IT services firms with US clients to small importers sourcing from Indian manufacturers.

## What it means for the diaspora

The summit's timing — falling during America's 250th independence celebrations — was no accident. It served as a reminder that Indian Americans are now deeply woven into the republic's economic and institutional fabric. From cybersecurity (Nikesh Arora at Palo Alto Networks) to pharmaceuticals (Reshma Kewalramani at Vertex) to AI policy in the White House (until Sriram Krishnan's recent departure), the community's fingerprints are everywhere.

What Mittal and Kwatra both articulated, in different registers, was a shift in how the diaspora should think about its own role. Not as beneficiaries of India's rise, and not as expatriates watching from abroad, but as structural connectors — the human infrastructure through which capital, ideas, and trust flow in both directions.

The USISPF itself has evolved from a lobbying shop into something closer to a bilateral chamber of commerce, with AI task forces, space trade missions, and tourism summits now on its roster. Its IX Summit drew business leaders from sectors as varied as defence, fintech, and clean energy.

Whether the trade deal materialises in weeks, as Mittal hopes, or continues to grind against the Pakistan tariff problem, the underlying trajectory seems clear. India and the US are building a $500 billion trade relationship, and the five million Indians living in America are not spectators. They are, as Mittal put it, the bridge."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Sitharaman Took India's Chequebook to France. She Is Ending the Trip by Meeting the Diaspora.",
        "subheadline": "India's finance minister co-chaired an economic dialogue in Aix-en-Provence, courted BNP Paribas and a cargo airship startup, and will wrap up her four-day visit with a community event for Indians in France — the quiet end of a loud trip.",
        "slug": make_slug("sitharaman-france-visit-diaspora-india-eu-trade-doubled"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Sitharaman's France visit concludes with a diaspora community interaction, connecting India's economic diplomacy directly to the 30,000-strong Indian community in France. India-France trade has doubled in a decade to €13.59 billion, and the India-EU FTA signed in January 2026 opens new pathways for NRIs across Europe.",
        "tags": ["nri", "diaspora", "sitharaman", "france", "india-eu", "trade"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "LiveMint", "url": "https://www.livemint.com/news/india/finance-minister-nirmala-sitharaman-begins-four-day-france-visit-11751402420178.html"},
            {"name": "DevDiscourse", "url": "https://www.devdiscourse.com/article/law-order/3382285-nirmala-sitharaman-begins-france-visit-to-boost-economic-ties"},
            {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/sitharaman-highlights-indias-investment-opportunities-in-talks-with-french-business-leaders"},
            {"name": "NewKerala", "url": "https://www.newkerala.com/news/2026/87178.htm"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/26/Am_11._April_2025_empfing_Au%C3%9Fenministerin_Beate_Meinl-Reisinger_die_indische_Finanzministerin_Nirmala_Sitharaman_in_Wien_%2854445397025%29_%28cropped%29.jpg",
        "image_caption": "Finance Minister Nirmala Sitharaman during a European engagement in 2025",
        "image_attribution": "Wikimedia Commons",
        "body": """Nirmala Sitharaman arrived in France on July 1 with an agenda that read like a sampler platter of India's economic ambitions: nuclear fusion, cybersecurity, cargo airships, and a pitch to some of Europe's biggest bankers. Four days later, she will close the visit the way Indian officials increasingly do on foreign trips — by sitting down with the local diaspora.

The community interaction, scheduled as the final event of her trip, is a small gesture that carries a growing subtext. India's engagement with its overseas citizens has quietly shifted from ceremonial flag-waving to something more transactional: the government wants the diaspora's money, expertise, and networks, and it is willing to show up in person to say so.

## The economic dialogue

The centrepiece of Sitharaman's visit was the India-France Economic and Financial Dialogue (EFD) in Aix-en-Provence, co-chaired with France's Minister of Economy Roland Lescure. The dialogue covered familiar ground — investment, technology, trade — but it came against a backdrop that makes the numbers harder to ignore.

India-France bilateral trade has more than doubled over the past decade, reaching €13.59 billion ($15.81 billion) in FY26. Indian exports to France alone amounted to €6.1 billion ($7.1 billion). Within the European Union, France is now India's third-largest trading partner, behind only the Netherlands and Germany.

And then there is the India-EU Free Trade Agreement, signed on January 27, 2026 — a deal that had been negotiated on and off for the better part of two decades before finally landing. For Indian professionals, students, and business owners across Europe, the FTA is expected to ease mobility, reduce tariffs on Indian goods, and open services markets that were previously difficult to crack.

## Courting global capital

Sitharaman held one-on-one meetings with senior executives from BNP Paribas, one of Europe's largest banks, and Flying Whales, a French startup building giant cargo airships for transporting heavy loads to remote areas without runways.

The Flying Whales meeting was the more eye-catching of the two. The company's president, Sébastien Bougon, briefed Sitharaman on sustainable PPP projects around the world and conveyed his company's intention to set up its entire manufacturing ecosystem with India as a key base. Sitharaman pointed him toward GIFT City's ship and aircraft leasing framework — a sign that India is increasingly trying to position itself as a manufacturing and services hub, not just a market.

The BNP Paribas conversation, meanwhile, underscored India's deepening financial integration with Europe. The Reserve Bank of India signed an MoU with the Banque de France in March 2026, covering joint projects in central banking, digital currencies, and financial regulation.

## The French connection

For Indians living in France — a community of roughly 30,000, with a wider population of Indian-origin residents reaching into the hundreds of thousands when you count PIOs and OCI holders — the visit carries personal resonance.

Just two weeks earlier, Prime Minister Modi himself addressed the Indian community at Salle Pleyel in Paris, praising the diaspora for "adding new colours" to the city and calling them a reflection of India's unity in diversity. That event drew large crowds and loud chants. Sitharaman's community event will be quieter, but arguably more substantive — a finance minister has more to say about tax treaties, NRE/NRO accounts, and investment frameworks than a prime minister delivering a rally speech.

## The ITER visit and what it signals

Sitharaman also visited ITER at Cadarache, the international nuclear fusion research facility involving more than 30 countries. India is one of the partners, and the visit signals Delhi's interest in positioning itself at the frontier of energy research — an area where Indian scientists and engineers, many of them trained or working abroad, could play a connecting role.

She followed that with a visit to Campus Cyber, France's national cybersecurity hub, where discussions focused on digital resilience — a growing priority for both countries as AI and digital infrastructure become central to economic governance.

## What NRIs in Europe should watch

The broader picture for Indians across Europe is one of expanding opportunity. The EU FTA means lower barriers. India-France trade is climbing. French companies are actively exploring Indian manufacturing bases. And the Indian government is making the effort — sending a finance minister, not just a cultural attaché — to sit with the diaspora and listen.

Whether that translates into tangible policy changes — easier FCNR deposit rules for European NRIs, faster OCI processing at French consulates, or dedicated investment corridors for returning diaspora — remains to be seen. But the direction is unmistakable. India is no longer content to be sentimentally connected to its overseas citizens. It wants to be commercially connected, and France is becoming one of the places where that connection is being built."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
