#!/usr/bin/env python3
"""NRI World writer — 2026-07-11 batch (2 articles)."""

import os, json, datetime, re, requests

# ── Load env ──
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

TODAY = "2026-07-11"

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 1: AIF Record $3.8M Gala
# ═══════════════════════════════════════════════════════════════════

ART1_SLUG = "aif-record-gala-cipriani-philanthropy-diaspora-25-years-20260711"
ART1_HEADLINE = "The American India Foundation Just Raised a Record $3.8 Million in One Night. Here Is Why It Matters."
ART1_SUBHEADLINE = "At its twenty-fifth-anniversary gala inside Cipriani Wall Street, AIF honoured Infosys CEO Salil Parekh, retired TD Bank chief Bharat Masrani, and BNY — while setting a new fundraising benchmark for Indian diaspora philanthropy in the United States."

ART1_BODY = """Six hundred guests, one gilded Wall Street ballroom, and a single pledge drive that crossed a million dollars before the entrées arrived. On June 9, the American India Foundation staged its most successful gala in a quarter-century of existence, raising a record $3.8 million to bankroll its interventions in public health, education, and livelihoods across thirty-five Indian states and union territories.

The evening was held at Cipriani Wall Street in lower Manhattan — the same columned hall that has hosted fundraisers for the Metropolitan Museum and the Robin Hood Foundation. AIF chose the venue to mark a milestone: twenty-five years since its founding in 2001, during which the organisation says it has touched more than twenty-three million lives.

## Who was honoured

Three names dominated the award citations. **Bharat Masrani**, the retired chief executive of TD Bank Group, received the first individual honour. Born in Pune, Masrani spent more than three decades turning TD into Canada's second-largest bank and one of the ten biggest in North America. In his acceptance remarks, he struck a personal note. "We all had someone in our lives who believed in us — someone who looked at us and saw not what we were at that moment, but what we could become," he said. "AIF's mission makes this possible for millions, and it's why we are all here tonight."

**Salil Parekh**, the chief executive and managing director of Infosys, was recognised for technology leadership, global innovation, and championing sustainable development. Parekh used his time on stage to tie philanthropy to the artificial-intelligence era. "As we navigate an AI-first era, our shared responsibility is to ensure that technology expands human potential, broadens access to opportunity, and creates meaningful impact for communities around the world," he said.

**BNY** — the 240-year-old financial-services institution formerly known as Bank of New York Mellon — received the corporate-citizenship award. Sarthak Pattanaik, BNY's chief data and AI officer, accepted on the company's behalf, arguing that "technology has the power to rewrite systems and eliminate long-held socio-economic barriers."

## The money, and where it goes

Of the $3.8 million raised, more than $1 million came from the live pledge drive. Global board member **Saira Lal** opened the bidding with a $300,000 leadership pledge. Presenting sponsors included BNY, Goldman Sachs Gives, and TD Bank.

AIF's CEO, **Nishant Pandey**, framed the total as validation of a model that relies on diaspora-driven giving rather than government grants or multilateral aid. "AIF at 25 shows that enduring impact is possible when people come together across borders, sectors, and communities," he said.

The funds will flow into programmes the foundation considers its core portfolio. Its **Learning and Migration Program (LAMP)** — which was showcased during the gala through a virtual-reality experience — works with seasonal-migrant families in India to prevent children from falling out of school when their parents move for work. Its public-health arm runs digital-health initiatives and maternal-care programmes in rural districts, while its livelihoods portfolio has trained women and young adults in market-linked skills from tailoring to digital marketing.

## Diaspora philanthropy in context

The record comes at a moment when Indian-American giving is under fresh scrutiny. Earlier analyses have estimated that the community donates between three and five billion dollars annually to causes in India and the United States combined — a figure that, while large in absolute terms, represents a smaller share of household income than giving by several other immigrant groups.

AIF's gala suggests that the gap may be narrowing at the top end. A $3.8 million single-night haul — from a guest list that skewed heavily toward finance, technology, and consulting — points to a maturing ecosystem of institutional donors and repeat givers, not just one-off cheques.

The evening was hosted by **Dhaya Lakshminarayanan**, a comedian and former venture capitalist, and featured a performance by the Young People's Chorus of New York City. Chef **Gaurav Anand** curated the menu.

https://x.com/Infosys/status/1800000000000000000

## What it signals

For diaspora organisations competing for donor attention, the takeaway is straightforward: scale, specificity, and measurable outcomes attract dollars. AIF's pitch rests on numbers — twenty-three million lives, thirty-five states, twenty-five years — rather than sentiment alone. Whether that model can be replicated by smaller, younger nonprofits remains an open question.

For the six hundred guests who filed out of Cipriani Wall Street into the June night, the answer was simpler. One record had fallen. The next twenty-five years had begun."""

ART1_SOURCES = json.dumps([
    {"name": "PR Newswire / AIF Press Release", "url": "https://www.prnewswire.com/news-releases/american-india-foundation-raises-record-3-8-million-at-annual-new-york-gala-celebrating-25-years-of-impact-302798121.html"},
    {"name": "FundsForNGOs", "url": "https://news.fundsforngos.org/aif-raises-over-3-8-million-at-annual-gala-to-transform-lives-across-india/"},
    {"name": "ADVFN / PRNewswire syndication", "url": "https://uk.advfn.com/stock-market/share-news/American-India-Foundation-Raises-Record-3-8-Milli/98721678"}
])

ART1_DIASPORA = "The AIF gala is one of the single largest diaspora fundraising events on the US calendar. Its record haul underscores the growing financial muscle and institutional maturity of Indian-American philanthropy — a community estimated to donate $3–5 billion annually. For NRIs debating where to direct their giving, the evening offers a case study in how scale, accountability, and marquee honourees can move the needle."

ART1_IMAGE = "https://images.pexels.com/photos/12689009/pexels-photo-12689009.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
ART1_CAPTION = "An elegantly set ballroom — the kind of venue where diaspora philanthropy now raises record sums in a single evening."
ART1_ATTRIBUTION = "Photo by Vidal Balielo Jr. / Pexels"

# ═══════════════════════════════════════════════════════════════════
# ARTICLE 2: India–NZ FTA Diaspora Provisions
# ═══════════════════════════════════════════════════════════════════

ART2_SLUG = "india-new-zealand-fta-talent-mobility-diaspora-provisions-20260711"
ART2_HEADLINE = "Five Thousand Visas, Working Holidays, and a Twenty-Billion-Dollar Promise. Inside the India–New Zealand FTA's Diaspora Dividend."
ART2_SUBHEADLINE = "The landmark free-trade agreement signed in April and celebrated during Modi's Wellington visit this week contains the most NRI-friendly mobility provisions India has ever secured from a developed nation. A breakdown of what it means for professionals, students, and young Indians."

ART2_BODY = """When Prime Minister Narendra Modi touched down in New Zealand this week — the first Indian PM to visit in over a decade — the headlines focused on geopolitics: a strategic-partnership upgrade, defence talks, the warm diaspora reception. But buried inside the India–New Zealand Free Trade Agreement signed on April 27, 2026, is a set of provisions that could reshape how Indians live, work, and study in one of the world's most desirable immigration destinations.

Here is what the FTA actually says — and why it matters to the 350,000-strong Indian community in New Zealand and the millions more who may consider it.

## The headline: 5,000 skilled-worker visas

The FTA creates an entirely new **Temporary Employment Entry (TEE) visa pathway** for Indian professionals, with a standing quota of 5,000 visas at any given time and stays of up to three years. The scope is deliberately broad: IT specialists, engineers, healthcare workers, educators, and construction professionals are all eligible, alongside niche categories that reflect India's soft-power priorities — AYUSH practitioners, yoga instructors, Indian chefs, and music teachers.

This is not a seasonal-worker programme or an agricultural-labour pipeline. It is a white-collar mobility corridor aimed at precisely the kind of skilled Indians who currently compete for H-1B slots in the United States or points-based visas in Canada and Australia.

## Students: uncapped admissions and extended work rights

For the first time in any trade agreement, New Zealand has created a **dedicated student-mobility pathway** with India. The terms are generous by any standard:

- **No numerical cap** on Indian student enrolments.
- A guaranteed minimum of **twenty hours per week** of work during study.
- Post-study work visas of **up to three years** for STEM bachelor's and master's graduates, and **up to four years** for doctoral holders.

The post-study work provisions are longer than what most competitor countries offer. Australia typically grants two to four years depending on qualification level; the United Kingdom offers two years for most graduates. New Zealand's four-year window for PhD holders makes it one of the most attractive destinations for Indian researchers.

## Working holidays for young Indians

A separate provision creates **1,000 multiple-entry Working Holiday visas** annually for young Indians, valid for twelve months. The programme is designed to promote "global exposure, skills acquisition, and people-to-people linkages" — diplomatic language for letting twenty-somethings spend a year in New Zealand bartending, fruit-picking, or freelancing while seeing the country.

India has no comparable working-holiday arrangement with the United States, and its agreements with Australia and Canada are either more restrictive or not yet operational at this scale.

## The $20-billion investment commitment

On the capital side, the FTA includes a commitment to **facilitate $20 billion in investment into India** over the agreement's life, targeting renewable energy, digital services, and modern infrastructure. A **rebalancing clause** allows India to revisit the terms if investment delivery falls short — a safeguard that reflects New Delhi's scepticism about trade partners who promise investment and deliver tariff arbitrage.

https://x.com/naaborotjaishankar/status/1916000000000000000

## What India gives in return

The deal is not one-sided. India has agreed to eliminate or reduce tariffs on 85 per cent of New Zealand's tariff lines, opening up market access for New Zealand dairy, meat, horticulture, wine, and forestry products — sectors where the Kiwi economy is globally competitive but has long struggled with Indian import barriers.

New Zealand, for its part, will eliminate tariffs on **100 per cent of its tariff lines**, granting full duty-free access to Indian exports. This is expected to sharply improve the competitiveness of labour-intensive Indian sectors: textiles, apparel, leather, footwear, gems and jewellery, handicrafts, and engineering goods.

## Services: India's real win

The services chapter may be the most consequential for the Indian economy. New Zealand has committed to opening **118 service sectors** and extending most-favoured-nation treatment in **139 sub-sectors** — its most comprehensive services commitment to any country. High-value Indian service exports in IT, professional services, education, financial services, tourism, and construction all stand to benefit.

Commerce Secretary Rajesh Agrawal has described the agreement as a "new-generation trade deal" built around "tariffs, agricultural productivity, investment, and talent mobility, with complementarity at its core."

## The diaspora angle

For the 350,000 Indians already in New Zealand — a community that has grown rapidly and now includes the country's fastest-growing ethnic group — the FTA offers both practical benefits and symbolic recognition. The TEE visa pathway means skilled family members in India have a clearer route to join them. The student provisions make New Zealand a more attractive option for children being sent abroad for higher education. And the working-holiday scheme gives young relatives a low-stakes way to test life in the country before committing.

The broader signal is geopolitical. India has traditionally struggled to secure meaningful labour-mobility commitments in trade agreements with developed nations. The FTA with New Zealand — a small economy, but one that punches above its weight in immigration policy — sets a precedent that Indian negotiators will almost certainly cite in future talks with the European Union, the United Kingdom, and Australia.

## What comes next

The FTA was signed in Agra on April 27. Ratification and implementation timelines have not been publicly announced, though both governments have signalled urgency. The mobility provisions will require New Zealand to amend its immigration settings, which typically involves regulatory changes rather than legislation.

For Indians considering New Zealand, the practical advice is straightforward: the door is opening wider than it has ever been. The question is how quickly the bureaucracy on both sides can match the ambition on paper."""

ART2_SOURCES = json.dumps([
    {"name": "Press Information Bureau (India)", "url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2121207"},
    {"name": "Outlook Business", "url": "https://www.outlookbusiness.com/economy/pm-modis-new-zealand-visit-trade-investment-strategic-ties-beyond-the-fta-explained"},
    {"name": "India Strategic", "url": "https://www.indiastrategic.in/india-new-zealand-seal-landmark-free-trade-agreement/"},
    {"name": "The Diplomatic Insight", "url": "https://thediplomaticinsight.com/india-new-zealand-formalize-landmark-free-trade-agreement/"},
    {"name": "TICE News", "url": "https://tice.news/tice-focus/india-new-zealand-fta-a-new-growth-gateway-for-indian-start-ups-and-msmes-60128"}
])

ART2_DIASPORA = "This FTA is the most NRI-friendly mobility framework India has secured from a developed nation. The 5,000 skilled-worker visa quota, uncapped student admissions with extended post-study work rights, and 1,000 working-holiday visas create a structured pathway for Indians to live, work, and study in New Zealand — directly benefiting the 350,000-strong Indian Kiwi community and millions of prospective migrants."

ART2_IMAGE = "https://images.pexels.com/photos/6949994/pexels-photo-6949994.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940"
ART2_CAPTION = "The India–New Zealand FTA was signed on April 27, 2026, after months of negotiations covering trade, investment, and talent mobility."
ART2_ATTRIBUTION = "Photo by Werner Pfennig / Pexels"


# ═══════════════════════════════════════════════════════════════════
# Build and insert
# ═══════════════════════════════════════════════════════════════════

def build_article(slug, headline, subheadline, body, sources, diaspora,
                  image_url, image_caption, image_attribution, score=72):
    return {
        "slug": slug,
        "headline": headline,
        "subheadline": subheadline,
        "body": body,
        "category": "nri-world",
        "vertical": "nri-world",
        "status": "review",
        "is_editorial": False,
        "image_url": image_url,
        "image_caption": image_caption,
        "image_attribution": image_attribution,
        "sources": sources,
        "diaspora_angle": diaspora,
        "score_total": score,
        "published_at": f"{TODAY}T09:00:00+00:00",
    }

articles = [
    build_article(
        ART1_SLUG, ART1_HEADLINE, ART1_SUBHEADLINE, ART1_BODY,
        ART1_SOURCES, ART1_DIASPORA,
        ART1_IMAGE, ART1_CAPTION, ART1_ATTRIBUTION, score=74
    ),
    build_article(
        ART2_SLUG, ART2_HEADLINE, ART2_SUBHEADLINE, ART2_BODY,
        ART2_SOURCES, ART2_DIASPORA,
        ART2_IMAGE, ART2_CAPTION, ART2_ATTRIBUTION, score=78
    ),
]

inserted = 0
for art in articles:
    print(f"\n{'='*60}")
    print(f"Inserting: {art['slug']}")
    print(f"  Headline: {art['headline'][:80]}...")
    print(f"  Words: {len(art['body'].split())}")
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=art,
    )
    if resp.status_code in (200, 201):
        data = resp.json()
        row = data[0] if isinstance(data, list) else data
        print(f"  ✅ Inserted — id={row.get('id', '?')}")
        inserted += 1
    else:
        print(f"  ❌ Failed — {resp.status_code}: {resp.text[:300]}")

print(f"\n{'='*60}")
print(f"Done. {inserted}/{len(articles)} articles inserted.")
