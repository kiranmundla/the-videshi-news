#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 14:30 UTC batch
Topics: 1) Pope Leo XIV's AI encyclical "Magnifica Humanitas" — from the Indian tech diaspora angle
        2) Xi hosted Pakistan PM + Army chief in Beijing on the same day Rubio was in New Delhi
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
from pathlib import Path

# ── Supabase config ──
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

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Pope Leo XIV's AI Encyclical — The Indian Tech Diaspora Angle
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("pope-leo-ai-encyclical-magnifica-humanitas-indian-tech-workers-silicon-valley")
headline1_prefix = "pope leo"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The Pope Just Published a 43,000-Word Document About Artificial Intelligence. He Compared It to the Tower of Babel. He Called for 'Disarming' It. And the People He Is Talking About Are Disproportionately Indian Americans Running the Industry From Silicon Valley.",
        "subheadline": "On Monday, Pope Leo XIV — the first American pope — released 'Magnifica Humanitas,' a 235-page encyclical that is the most significant institutional response to artificial intelligence by any global religious body. He presented it personally at the Vatican alongside Chris Olah, co-founder of Anthropic, the AI company currently in a legal dispute with the Trump administration over military use of its technology. The Pope said AI 'threatens to normalize an anti-human vision' and that its development cannot remain in the control 'of a few.' He prescribed the 'disarmament' of AI — not rejecting the technology but 'preventing it from dominating humanity' and 'freeing technology from monopolistic control.' He compared the current AI moment to the biblical Tower of Babel. He declared the 'just war' theory outdated. He apologized for the Catholic Church's historic role in slavery. And he did all of this knowing that the industry he was addressing is led, in disproportionate measure, by Indian Americans: Sundar Pichai at Google, Satya Nadella at Microsoft, Arvind Krishna at IBM, Shantanu Narayen at Adobe. The encyclical arrives as India itself positions for a central role in AI — Jaishankar referenced AI cooperation with the US just yesterday in New Delhi — and as hundreds of thousands of Indian H-1B workers build the systems the Pope wants regulated.",
        "slug": slug1,
        "category": "news",
        "vertical": "technology",
        "diaspora_angle": "If you are an Indian engineer at Google, Microsoft, Meta, Amazon, or any of the AI labs in the Bay Area, Seattle, or New York, the Pope just wrote a 43,000-word document about what you do for a living. He did not mention you by name, but he did not need to. Indian Americans hold the CEO positions at the two largest AI-investing companies in the world (Pichai at Alphabet, Nadella at Microsoft). Indian-origin engineers comprise an estimated 30-40 percent of the technical workforce at major AI labs. Indian H-1B holders are disproportionately concentrated in the machine learning, data science, and AI engineering roles that the encyclical addresses. When the Pope says AI development cannot remain in the hands 'of a few,' he is describing an industry where the few include a remarkable concentration of people who grew up in Hyderabad, Chennai, Bengaluru, and Delhi. The irony is layered. Indian culture valorizes technology as a pathway to prosperity — the IIT-to-Silicon-Valley pipeline is a national mythology. The Pope is now saying that the endpoint of that pipeline — the AI systems built by the graduates of that pipeline — poses an existential risk to human dignity. He is not wrong to worry. But the Indian diaspora's relationship with AI is more complicated than the encyclical acknowledges. For many Indian families in America, AI is not an abstract philosophical question. It is the H-1B sponsor. It is the reason the mortgage gets paid. It is the industry that justifies the $200,000 in student loans. It is the career that makes the sacrifice of leaving India meaningful. When the Pope calls for 'disarming' AI, he is asking for something that, if implemented through regulation, could directly affect the employment prospects, visa sponsorship, and economic stability of hundreds of thousands of Indian American families. That does not make his concerns wrong. But it makes them personal in a way that the encyclical, written from the Vatican, does not fully grasp.",
        "tags": ["Pope Leo XIV", "AI", "Magnifica Humanitas", "encyclical", "Silicon Valley", "Indian Americans", "Sundar Pichai", "Satya Nadella", "Arvind Krishna", "H-1B", "Anthropic", "Chris Olah", "Vatican", "regulation", "Tower of Babel", "technology", "just war", "Trump", "NRI"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "CNN — Pope Leo warns of AI fueling warfare in first major theological document", "url": "https://www.cnn.com/2026/05/25/europe/pope-leo-ai-encyclical-magnifica-humanitas-intl"},
            {"name": "Wall Street Journal — Pope Leo Compares AI Threat to Biblical 'Tower of Babel'", "url": "https://www.wsj.com/world/pope-leo-ai-encyclical-magnifica-humanitas-tower-babel"},
            {"name": "Reuters — Pope Leo urges world to 'slow down' on AI in fervent first manifesto", "url": "https://www.reuters.com/world/pope-leo-encyclical-magnifica-humanitas-ai-2026-05-25/"},
            {"name": "Le Monde — Pope Leo XIV calls for 'disarming AI'", "url": "https://www.lemonde.fr/en/religions/article/2026/05/25/pope-leo-xiv-calls-for-disarming-ai"},
            {"name": "Wikipedia — Magnifica humanitas", "url": "https://en.wikipedia.org/wiki/Magnifica_humanitas"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_iso,
        "body": """On Monday morning in Vatican City, Pope Leo XIV broke with centuries of tradition. Rather than delegating the presentation of his first encyclical to a cardinal or senior church official, the first American pope walked to the podium himself, stood before journalists and theologians, and introduced a 235-page document about artificial intelligence.

Beside him was Chris Olah, co-founder of Anthropic, the AI company that has been locked in a legal dispute with the Trump administration over the use of its technology in military and defense operations. The pairing was deliberate — the spiritual leader of 1.4 billion Catholics standing alongside a technologist whose company is at the center of the debate over whether AI should be used in warfare.

The document is called "Magnifica Humanitas" — Magnificent Humanity. It is 43,000 words long. It compares the current AI moment to the biblical Tower of Babel. It calls for the "disarmament" of artificial intelligence. And it is, according to Vatican officials, "the most significant institutional response" to AI by any major global religious body.

## What the Pope Actually Said

The encyclical's core argument is that AI "threatens to normalize an anti-human vision" and that its development cannot remain in the control "of a few" private actors. The Pope calls for "robust legal frameworks, independent oversight, informed users and a political system that does not abdicate its responsibility."

He prescribed what he calls the "disarmament" of AI — a phrase he carefully defined not as the rejection of technology but as "preventing it from dominating humanity" and "freeing technology from monopolistic control and opening it to discussion and debate, therefore making it human-friendly."

The Pope said that every AI system "embodies choices and priorities through what it measures, ignores and optimizes, and how it classifies people and situations." He argued that AI cannot be considered "morally neutral" — a direct challenge to the Silicon Valley position that technology is a tool and its morality depends on its use.

He drew on the biblical story of the Tower of Babel, in which humanity attempted to build a structure reaching heaven using a single language and a single power. The Pope said AI risks creating a similar dynamic — a technology built by a concentrated group using a shared technical language that "dominates and ultimately dehumanizes." He insisted instead that diverse perspectives and communities must contribute to AI's development.

The encyclical also critiqued "transhumanism" — the idea that technology can help humans overcome biological limitations like aging — and "posthumanism," which questions the distinctiveness of human beings and blurs the boundaries between humans and machines. For the Pope, these are not merely philosophical positions. They are threats to the Catholic understanding of human dignity.

## The 'Just War' Doctrine Is Dead

In a section that drew immediate attention from foreign policy analysts, the Pope declared the traditional "just war" theory — a four-pronged Christian doctrine dating to Augustine that outlines when military force is morally justified — to be "now outdated."

Military force can only be used for "self-defense in the strictest sense," the Pope wrote, adding that the "construction of a world in a state of perpetual conflict is an evil and must be named for what it is."

This is not an abstract theological position. Pope Leo has been in an escalating public dispute with the Trump administration over the Iran war. After the Pope fiercely criticized joint US-Israeli strikes on Iran, Vice President JD Vance warned that the Pope should "be careful when he talks about matters of theology." The encyclical's repudiation of just war theory is, in part, a direct theological response to Vance and to any attempt to use religious language to justify the conflict.

The Pope also warned that AI-powered autonomous weapons systems have advanced "practically beyond any human reach to govern them" — a statement that carries particular weight given Anthropic's own dispute with the Trump administration over military AI applications.

## Why This Is an Indian American Story

At the Vatican on Monday, Chris Olah said that decisions about AI "should not be left to people in the industry." He listed three principles requiring collective resolution: a "duty to the global poor," "moral imagination and ambition," and the "need for discernment."

"Every frontier AI lab, including Anthropic, operates inside a set of incentives and constraints that can sometimes conflict with doing the right thing," Olah told the audience. "If we want this technology to go well, it is enormously important that there be people outside those incentives who are willing to be our earnest, thoughtful critics."

The people inside those incentives are, in remarkable measure, Indian Americans.

Sundar Pichai leads Alphabet, Google's parent company, which is investing $75 billion in AI infrastructure in 2026 alone. Satya Nadella leads Microsoft, which has invested $13 billion in OpenAI and is embedding AI across every product. Arvind Krishna leads IBM, which has pivoted its entire business model toward enterprise AI. Shantanu Narayen leads Adobe, whose AI-powered creative tools are transforming how images, video, and text are produced.

Below the C-suite, the concentration deepens. Indian-origin engineers are estimated to comprise 30-40 percent of the technical workforce at major AI labs. The H-1B visa pipeline that feeds these companies draws heavily from India's IIT system and engineering colleges. The machine learning teams at Google Brain, DeepMind, Meta AI, and Microsoft Research include substantial contingents of Indian-born researchers.

When the Pope says AI must not remain in the hands of "a few," he is describing a reality where the few include a striking concentration of people from Hyderabad, Chennai, Bengaluru, Mumbai, and Delhi.

## The Cultural Contradiction

Indian culture valorizes technology as a pathway to prosperity. The IIT-to-Silicon-Valley pipeline is a national mythology — the engineering entrance exam as gateway to a middle-class American life, the H-1B visa as the document that makes the sacrifice of emigration meaningful.

The Pope is now saying that the endpoint of that pipeline — the AI systems built by the graduates of that system — poses a risk to human dignity that demands collective intervention and regulatory constraint.

He is not wrong to raise concerns. The concentration of AI development in a handful of companies, the lack of diverse perspectives in training data and model design, the use of AI in surveillance, autonomous weapons, and social manipulation — these are real problems that the industry has been slow to address.

But the encyclical, written from the Vatican, does not grapple with the economic reality of the people building these systems. For hundreds of thousands of Indian American families, AI is not an abstract philosophical question. It is the H-1B sponsor. It is the reason the mortgage in Cupertino or Bellevue or Redmond gets paid. It is the industry that justifies the $200,000 in student loans. It is the career that makes the sacrifice of leaving India meaningful.

When the Pope calls for "disarming" AI, he is asking for something that, if translated into regulation — hiring freezes, development moratoriums, capability restrictions — could directly affect the employment prospects, visa sponsorship, and economic stability of the very community that built the technology he is concerned about.

This is not a reason to dismiss the encyclical. It is a reason to take it seriously on terms that the Indian diaspora understands: the question is not whether AI should be regulated, but who bears the cost of regulation, and whether a regulatory framework designed by governments and religious institutions will account for the people — many of them immigrants, many of them on temporary visas, many of them one layoff away from a 60-day clock — who actually build the technology.

## India's Own Position

The encyclical arrives at a moment when India itself is positioning for a central role in AI governance. Just yesterday in New Delhi, External Affairs Minister S. Jaishankar referenced the AI Impact Summit held in New Delhi in February and told US Secretary of State Marco Rubio that "as India's semiconductor and AI capabilities advance, this cooperation will be even more prominent in days to come."

India has joined the US-led Pax Silica initiative on semiconductor supply chains and is part of the FORGE critical minerals framework. The Modi government's approach to AI has been distinctly different from the Pope's — emphasizing opportunity, investment, and national capability rather than regulation and restraint.

India's 1.4 billion people represent both the largest potential market for AI-powered services and the largest population that could be affected by AI-driven job displacement. The tension between these two realities — AI as economic opportunity and AI as existential risk — is one that the Indian government has not yet resolved, and one that the encyclical forces into sharper relief.

For Indian Americans working in AI, the Pope's document creates an unusual moment of reflection. The technology that provides their livelihood, that funds their children's education, that powers their visa applications, that defines their professional identity — that technology is now the subject of the most significant theological critique of the 21st century.

The Pope signed "Magnifica Humanitas" on May 15, the 135th anniversary of Leo XIII's "Rerum Novarum," the 1891 encyclical on workers' rights during the industrial revolution that laid the foundation of Catholic social teaching. Leo XIV told cardinals that he hoped to offer the Church's social teaching in response "to another industrial revolution."

Whether the people building that revolution — many of them from a civilization that predates the Catholic Church by millennia — will find his framework relevant is a question the encyclical leaves open. But the conversation has begun, and the Indian diaspora is at its center whether it wants to be or not.

## The Slavery Apology

In a section that received less attention but carries historical weight, Pope Leo offered a formal apology for the Catholic Church's role in legitimizing slavery. He called slavery a "wound in Christian memory" and expressed sorrow for the enslaved, marking the most explicit papal admission of institutional responsibility for the practice.

The apology carries particular resonance for the global South, including India, where the Catholic Church's colonial-era presence was intertwined with Portuguese and British imperial power in Goa, Kerala, and other regions. The Pope's willingness to confront institutional complicity — even centuries later — may signal an approach to AI governance that is more self-aware than the industry's own reckoning with its biases and harms.

## What Happens Next

The encyclical is a teaching document, not legislation. It cannot compel governments to regulate AI or companies to change their practices. But papal encyclicals have influenced policy before — Pope Francis's 2015 "Laudato Si'" on the environment helped build momentum for the Paris climate accord.

Pope Leo will likely hope "Magnifica Humanitas" serves a similar catalytic function. The Vatican has already established a cross-department commission on AI, and the Pope's decision to present the document alongside an AI company co-founder signals an intention to engage directly with the industry rather than simply criticize from the margins.

For the Indian tech community — whether in Bangalore building AI for TCS and Infosys, or in Mountain View building it for Google and Meta — the Pope's words pose a question that transcends theology: What does it mean to build the most powerful technology in human history, and who gets to decide how it is used?

The answer, the Pope suggests, should not be left to the builders alone. The builders, in significant measure, are from India. And they now have a 43,000-word document to reckon with."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Xi Hosted Pakistan in Beijing While Rubio Was in New Delhi
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("xi-jinping-pakistan-shehbaz-sharif-beijing-unbreakable-rubio-india-new-delhi")
headline2_prefix = "xi jinping"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "While Rubio Was in New Delhi Talking About Strategic Partnership, Xi Was in Beijing Hosting Pakistan's Prime Minister and Army Chief. He Called Their Friendship 'Unbreakable.' The Optics Were Not Accidental.",
        "subheadline": "On Monday, two diplomatic meetings took place simultaneously on two different continents. In New Delhi, India's External Affairs Minister S. Jaishankar hosted US Secretary of State Marco Rubio for the second day of bilateral talks — covering trade, defense, energy, AI, critical minerals, and the Iran situation — ahead of Tuesday's Quad Foreign Ministers' Meeting. In Beijing, Chinese President Xi Jinping greeted Pakistani Prime Minister Shehbaz Sharif and Pakistan Army chief General Asim Munir at the Great Hall of the People. Xi called the China-Pakistan friendship 'unbreakable.' Sharif called China and Pakistan 'iron brothers' with a relationship 'next to none.' Asim Munir had just returned from Tehran. And Xi praised Pakistan's 'constructive role' in the Iran peace mediation that Washington has also acknowledged. The parallel meetings expose the geometric reality of South Asian geopolitics in 2026: India aligns with the US to counterbalance China; Pakistan deepens its alignment with China while simultaneously serving as Washington's mediator with Tehran; and China courts Pakistan precisely because India's strategic partnership with America makes an alternative necessary. For NRIs watching from San Jose or Edison, the message is clear — the neighborhood you left has never been more diplomatically complicated.",
        "slug": slug2,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "For Indian Americans who grew up hearing that Pakistan is India's primary security threat and China its strategic rival, Monday's parallel diplomacy in New Delhi and Beijing crystallizes a reality that is simultaneously alarming and familiar. India is deepening its partnership with the world's most powerful nation. Pakistan is deepening its partnership with the world's second most powerful nation. Both partnerships are, in part, responses to each other. The India-US Quad architecture and the China-Pakistan 'all-weather' partnership are mirror images — each justified by the other's existence, each strengthened by the other's growth. For NRI families, this has practical implications beyond geopolitics. The CPEC corridor that Xi and Sharif discussed runs through Pakistan-occupied Kashmir — territory India claims. US defense partnerships with India may accelerate technology transfer but will also invite Chinese counter-moves through Pakistan. Pakistan's role as Iran mediator gives it diplomatic leverage that complicates India's own multi-alignment approach that Jaishankar articulated yesterday. And the deepening of all these relationships makes a broader South Asian peace settlement — the kind that would allow easier travel between India and Pakistan, lower defense spending, and create economic opportunities across the subcontinent — further away than ever. The Indian diaspora in America is uniquely positioned in this geometry. You live in the country that is India's strategic partner. You work in industries (tech, defense, energy) that are the substance of that partnership. And you watch, from 8,000 miles away, as the neighborhood you left rearranges itself around the choices your adopted country and your homeland are making together.",
        "tags": ["Xi Jinping", "Pakistan", "Shehbaz Sharif", "Asim Munir", "China", "CPEC", "India", "Rubio", "Jaishankar", "Quad", "New Delhi", "Beijing", "geopolitics", "Iran mediation", "all-weather partnership", "NRI", "defense", "South Asia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Reuters — Xi hails 'unbreakable' Pakistan ties, praises role in Iran peace efforts", "url": "https://www.reuters.com/world/asia-pacific/chinas-xi-meets-pakistan-pm-sharif-beijing-state-media-reports-2026-05-25/"},
            {"name": "MEA India — Transcript of Joint Press Conference by EAM Dr. S Jaishankar and US Secretary of State Marco Rubio", "url": "https://www.mea.gov.in/media-briefings.htm?dtl/41227/Transcript_of_Joint_Press_conference_by_EAM_Dr_S_Jaishankar_and_US_Secretary_of_State_Marco_Rubio_May_24_2026"},
            {"name": "Foreign Policy Journal — Marco Rubio Arrives in India for Quad Meeting as US Scrambles to Repair Tariff-Damaged Relations", "url": "https://www.foreignpolicyjournal.com/2026/05/24/marco-rubio-arrives-in-india-for-quad-meeting-as-us-scrambles-to-repair-tariff-damaged-relations/"},
            {"name": "Reuters — Global tensions set to stalk Singapore's flagship defence summit", "url": "https://www.reuters.com/world/global-tensions-set-stalk-singapores-flagship-defence-summit-2026-05-25/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now_plus1,
        "body": """On Monday morning in New Delhi, India's External Affairs Minister S. Jaishankar stood at a podium in Hyderabad House alongside US Secretary of State Marco Rubio. They spoke about strategic partnership, defense cooperation, energy trade, critical minerals, AI collaboration, and the Iran situation. Rubio called India "one of our most important strategic partners in the world." Jaishankar outlined a five-point framework for India's foreign policy: dialogue, maritime freedom, respect for international law, opposition to economic coercion, and trusted partnerships.

On Monday morning in Beijing, Chinese President Xi Jinping stood at the Great Hall of the People alongside Pakistani Prime Minister Shehbaz Sharif and Pakistan Army chief General Asim Munir. Xi called the China-Pakistan friendship "unbreakable." Sharif called China and Pakistan "iron brothers" with a relationship "next to none." Munir had just returned from Tehran, where he had met Iranian leadership as part of Pakistan's mediation of the Iran conflict.

The parallel was not accidental. It was a geometric statement about how power works in South Asia in 2026.

## The New Delhi Meeting

Rubio's four-day visit to India — his first as Secretary of State — covered Kolkata, Agra, Jaipur, and New Delhi. He was the first US Secretary of State to visit Kolkata in nearly fourteen years. His first stop was the Missionaries of Charity headquarters, Mother Teresa's organization, accompanied by US Ambassador Sergio Gor.

In New Delhi, the substance was dense. Jaishankar told reporters that the two sides discussed:

**Trade:** An interim trade agreement is close to final text. Jaishankar said he spoke about "the value of concluding, at an early date, the final text of the interim agreement regarding reciprocal and mutually beneficial trade." An Indian team visited Washington recently; a US trade representative delegation is expected in India soon. Rubio said he believes "we're going to wind up with a trade agreement between the United States and India that's going to be enduring."

**Defense:** The 10-year major defense partnership framework agreement was recently renewed. A comprehensive underwater domain awareness roadmap was also signed. Jaishankar emphasized the 'Make in India' approach — signaling that India wants defense technology co-production, not just procurement.

**Energy:** Both sides welcomed the expansion in energy trade. Jaishankar noted that "diversified supplies are at the heart of energy security for India" — a diplomatic way of saying India will continue buying oil from wherever it can while increasing US purchases. Nuclear energy cooperation was discussed, with the Shanti Act opening new possibilities.

**Critical Minerals and AI:** India has joined the US-led Pax Silica semiconductor initiative and the FORGE critical minerals framework. Jaishankar referenced the AI Impact Summit in New Delhi in February and said semiconductor and AI cooperation "will be even more prominent in days to come."

**Visas:** Jaishankar directly raised "challenges that legitimate travelers face in respect of visa issuance" — a diplomatic reference to H-1B, F-1, and J-1 visa restrictions that have caused deep anxiety in the Indian community. Rubio responded that the US immigration system is being "modernized" globally, that the changes are "not India-specific," and that after a "period of transition" the system would be "even more beneficial than the previous system was to people from India." He acknowledged a "disproportionate impact on a place like India that provides so many high-skilled workers."

**Pakistan:** When asked whether the US engagement with Pakistan comes at India's expense, Rubio said: "I don't view our relation with any country in the world as coming at the expense of our strategic alliance with India."

## The Beijing Meeting

While those words were being spoken in New Delhi, Xi Jinping was offering a different reassurance in Beijing.

"No matter how the international situation changes, China always prioritises the development of China-Pakistan relations in its neighbourhood diplomacy," Xi told Sharif at the Great Hall of the People.

Sharif reciprocated in kind, calling the relationship between the two countries one that is "next to none." He was accompanied by Army chief Asim Munir — a detail of significant diplomatic weight. In Pakistan, the Army chief's presence at a foreign leader meeting signals that the military establishment, which has historically driven Pakistan's China and security policy, is fully aligned with the civilian diplomatic agenda.

Munir had recently returned from Tehran, where he had held meetings with Iranian leadership as part of Pakistan's mediation role in the US-Iran conflict. Xi acknowledged this directly: "I know that you have just returned from Iran and made positive efforts for the current peace. We still appreciate the constructive role played by Pakistan."

This praise positions Pakistan in an extraordinary diplomatic place. It is simultaneously being lauded for its peacemaking by both the United States — which has credited Pakistan's mediation for progress in the Iran talks — and by China, which has its own close relationship with Tehran.

## The Geometry

The parallel meetings expose the structural logic of South Asian geopolitics in 2026.

**India aligns with the US to counterbalance China.** The Quad — bringing together the US, India, Japan, and Australia — meets Tuesday in New Delhi. Its agenda covers freedom of navigation in the South China Sea, cybersecurity, critical mineral supply chains, and coordination on the Iran crisis. The Quad exists, fundamentally, because China's military and economic expansion in the Indo-Pacific requires a multilateral response.

**Pakistan deepens its alignment with China.** The China-Pakistan Economic Corridor (CPEC), a $62 billion infrastructure project that is the flagship of Xi's Belt and Road Initiative, runs through Pakistan-occupied Kashmir — territory India claims. CPEC gives China a strategic land route to the Arabian Sea, bypassing the Strait of Malacca chokepoint that India and the US could theoretically interdict. For Pakistan, CPEC provides desperately needed infrastructure investment and deepens the economic ties that underpin the military partnership.

**Pakistan simultaneously serves as Washington's Iran mediator.** This is the element that most complicates India's position. Pakistan hosted the Islamabad mediation talks between Washington and Tehran, relaying proposals and messages when tensions escalated. Pakistan's role gives it diplomatic leverage with the United States at a moment when India thought its own relationship with Washington was the defining partnership of the region.

**China courts Pakistan precisely because India's US partnership makes an alternative necessary.** Every expansion of the Quad, every US-India defense agreement, every critical minerals partnership strengthens Beijing's incentive to deepen its own alternative network. Pakistan is the cornerstone of that network in South Asia. The logic is self-reinforcing.

## The Jaishankar Doctrine

At the press conference on Saturday, Jaishankar articulated what he called India's approach to managing multiple relationships simultaneously. A journalist asked whether India's ability to maintain strong ties with the US, Israel, Iran, and the Gulf countries simultaneously was an example of "multi-alignment."

Jaishankar accepted the framing. "India would be one of the very few countries who has very good relations, very strong relations with the United States, with Israel, with Iran, and with the Gulf countries," he said. "We don't look at it as a zero-sum game."

He outlined India's principles: peace and stability in the region, welfare of the diaspora, lower energy prices, safe maritime commerce, and open markets.

This is the Jaishankar Doctrine in practice — India as a relationship-portfolio manager, maintaining diverse positions that can be activated depending on circumstances, refusing to collapse all of its diplomacy into a single alliance.

The challenge is that Pakistan is playing a version of the same game. Sharif maintained relationships with both Washington and Beijing simultaneously. Pakistan's Iran mediation gave it value to the United States. Its CPEC partnership gave it value to China. And the Army chief's presence in both Tehran and Beijing within weeks demonstrated that Pakistan's security establishment is managing its own multi-alignment with considerable skill.

## What This Means for India

India's strategic community has long argued that Pakistan punches above its weight diplomatically — that a country with India's GDP would be able to marginalize Pakistan through sheer economic gravity. The Monday parallel suggests that this has not happened.

Pakistan remains central to China's regional strategy. It remains useful to Washington's Iran diplomacy. And its Army chief moves between Tehran and Beijing with a fluency that India's own security establishment, which maintains more formal protocols and slower decision-making cycles, sometimes struggles to match.

For India, the Quad meeting on Tuesday will be the immediate test. The joint statement is expected to cover freedom of navigation, cybersecurity, critical minerals, and the Hormuz situation. If the statement is strong and specific — naming threats, committing resources, setting timelines — it will demonstrate that the India-US partnership produces institutional results, not just diplomatic language.

If it is general and aspirational, Beijing will note the gap between rhetoric and reality. And the "unbreakable" friendship that Xi described on Monday will look less like a diplomatic courtesy and more like a structural counterweight that India has not yet figured out how to neutralize.

## The View From 8,000 Miles

For the Indian diaspora in America, Monday's parallel diplomacy crystallizes a reality that is simultaneously reassuring and unsettling.

The reassurance: India's partnership with the United States has never been deeper. Rubio called it one of America's most important strategic alliances. The trade deal is close. Defense cooperation is expanding. Energy trade is growing. Critical minerals and AI partnerships are accelerating. By every metric, the India-US relationship is on an upward trajectory.

The unsettlement: Pakistan is not being squeezed out. China is not pulling back. The neighborhood that NRI families left — the one they worry about when their parents are in Delhi or Mumbai or Bengaluru, the one they check the news about when tensions spike — is arranging itself into two competing blocs with escalating commitments.

India is in one. Pakistan is in the other. The US is leading one. China is leading the other. And on Monday, both meetings happened on the same day, at the same time, in capital cities separated by 3,800 kilometers and 30 years of unresolved conflict.

The diplomacy is sophisticated on all sides. The geometry is elegant. The underlying problem — two nuclear-armed neighbors that cannot find a way to coexist peacefully — remains exactly where it was before either meeting began."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Source images for articles ──
PEXELS_KEY = ""
pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "pexels" in k.lower():
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    return []

def get_pexels_image_url(query):
    photos = search_pexels(query)
    if photos:
        return photos[0]["src"]["large2x"]
    return None

image_queries = {
    slug1: "vatican pope press conference technology artificial intelligence",
    slug2: "world flags diplomacy summit meeting geopolitics",
}

for art in articles:
    slug = art["slug"]
    query = image_queries.get(slug, "")
    if not query:
        continue
    img_url = get_pexels_image_url(query)
    if img_url:
        try:
            sb_patch("p2_articles", {"id": f"eq.{art['id']}"}, {"image_url": img_url})
            print(f"🖼️  Image set for {slug}: {img_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Image PATCH failed for {slug}: {e}")
    else:
        print(f"⚠️  No Pexels image found for {slug}")

# ── Score decay for news articles older than 12h ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

# ── Git commit & push ──
try:
    repo = Path.home() / "workspace" / "the-videshi-news"
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
    msg = f"news: Pope Leo AI encyclical + Xi-Pakistan parallel diplomacy ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
