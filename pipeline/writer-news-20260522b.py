#!/usr/bin/env python3
"""Videshi Writer — 4 fresh NEWS articles for 2026-05-22 (afternoon batch)
Focus: diaspora news, geopolitics, economy
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone

# ── Supabase config ──
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

def make_slug(headline, date_suffix="20260522"):
    slug = headline.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: NEWS — UK Launches Anti-Hindu Hate Monitor
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "Britain Just Launched Its First Anti-Hindu Hate Monitor. The Data It Collects Could Change How 1.2 Million Hindus Are Protected.",
    "subheadline": "The new platform, backed by the Hindu Council UK and a London Assembly member, addresses a blind spot in Britain's hate crime tracking — one that has left Hindu, Jain, and Dharmic communities statistically invisible for years.",
    "slug": make_slug("uk-anti-hindu-hate-monitor-launch-data-protection"),
    "category": "news",
    "vertical": "diaspora",
    "diaspora_angle": "For the 1.2 million Hindus in Britain — and for NRIs in America watching the same pattern of underreported hate crimes in their own communities — this platform is both a milestone and a mirror. If the UK can build a systematic reporting tool, the question is why the US hasn't.",
    "tags": ["UK", "anti-Hindu hate", "hate crimes", "Hindu Council UK", "ICfS", "diaspora", "Krupesh Hirani", "Metropolitan Police"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Devdiscourse — New Anti-Hindu Hate Monitor platform launched in UK", "url": "https://www.devdiscourse.com/article/law-order/3917151-new-anti-hindu-hate-monitor-platform-launched-in-uk"},
        {"name": "Hindu Council UK — AHHM by ICfS", "url": "https://hinducounciluk.org"},
        {"name": "USA Today — New Anti-Hindu Hate Monitor Launched in UK", "url": "https://usatodaycom.com"},
        {"name": "ThisDay — Rise in religious hate crimes", "url": "https://thisday.com.ng"}
    ]),
    "score_total": 79,
    "status": "published",
    "published_at": now,
    "body": """Britain has launched its first dedicated platform for reporting and tracking anti-Hindu hate crimes, an initiative that its organisers hope will force the country's law enforcement and policymaking apparatus to confront a problem it has largely failed to measure.

The Anti-Hindu Hate Monitor, or AHHM, went live this week as a project of the International Centre for Sustainability's Future of Faith Desk in London, with backing from the Hindu Council UK. The platform allows individuals to report incidents across nine categories — from extreme violence and assault to online abuse and discrimination — and aims to build the kind of systematic dataset that has never existed for Britain's Hindu community.

"Currently, there is no way of reporting these hate crimes," said Krupesh Hirani, London Assembly Member for Brent and Harrow, a north-west London constituency that is home to one of the city's largest Hindu populations. "My next task is to make sure that the data that's being reported and monitored is recognised by the Metropolitan Police."

## The Invisible Community

The numbers tell a story of structured neglect. Under Home Office statistics released last October, religiously aggravated offences in England and Wales were dominated by anti-Muslim hate crimes at 4,478 incidents (45 per cent of the total), followed by 2,873 anti-Jewish incidents (29 per cent). Anti-Hindu crimes accounted for just 182 reported incidents — 2 per cent of the total.

But that number almost certainly understates the problem. Community leaders and researchers have long argued that Hindus in Britain dramatically underreport hate incidents, in part because no dedicated reporting mechanism existed, and in part because many victims are unsure whether what they experienced qualifies as a hate crime under British law.

The ICfS's own research, published in a 2025 report titled "Investigating the Perceptions of Anti-Hindu Hate and Discrimination in the UK," identified a significant gap between lived experience and official statistics. London alone saw a 23 per cent increase in faith-based hate offences compared to the previous year, yet the Hindu-specific share remained suspiciously flat — suggesting not that incidents weren't happening, but that they weren't being captured.

## What the Platform Does

The AHHM classifies incidents into nine reportable categories: Extreme Violence, Assault, Damage and Desecration of Property, Threats, Abusive Behaviour, Anti-Hindu Literature, Hate Speech, Discrimination, and Online Content or Abuse. The platform covers not only those who identify as Hindu but also Jain communities and adherents of other Dharmic traditions who face similar patterns of targeting.

Dipen Rajyaguru, Director of Equality and Inclusion at Hindu Council UK, urged temples, organisations, youth groups, and community leaders to share the platform widely. "By working together, we can strengthen understanding, improve safeguarding, and help ensure that all communities are treated with dignity and respect," he said.

The data collected will be shared with the Home Office, law enforcement agencies, and local authorities — giving policymakers, for the first time, a community-generated evidence base to complement official crime statistics.

## Why This Matters for NRIs in America

For Indian-Americans watching from across the Atlantic, the UK's initiative highlights a gap that exists — arguably more acutely — in the United States. The FBI's annual hate crime statistics categorise religious bias incidents by faith, but the data is notoriously incomplete. Many police departments do not participate in the reporting programme, and there is no dedicated federal mechanism for Hindu, Jain, or Sikh communities to report incidents outside the general hate-crime framework.

The Hindu American Foundation has documented a rise in anti-Hindu incidents in the US, from temple vandalism in California to harassment of students at universities. But without a systematic reporting tool, the scale of the problem remains anecdotal rather than statistical — which makes it easy for policymakers to deprioritise.

Britain's AHHM is not a silver bullet. It depends on community adoption, police willingness to engage with the data, and sustained funding. But it represents something that has been missing from the conversation about religious hate crimes in the West: the idea that a community's safety begins with its ability to be counted.

## The Broader Context

The launch comes at a politically charged moment in the UK. Immigration and multiculturalism have become central issues in British politics, and Hindu communities — particularly those with roots in India, East Africa, and the Caribbean — have found themselves navigating a landscape where anti-immigrant sentiment and religious prejudice increasingly overlap.

The Leicester disturbances of 2022, which saw clashes between Hindu and Muslim communities following an India-Pakistan cricket match, served as a wake-up call for many British Hindus who had previously considered themselves immune from the kind of communal tensions that define politics in South Asia. Since then, community organisations have pushed for better data, better policing, and better representation in the structures that govern how hate is tracked and addressed.

The AHHM is the first concrete institutional response to that push. Whether it succeeds will depend on whether the community uses it — and whether the authorities take what it produces seriously.""",
    "word_count": 800,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 2: NEWS — Bhangra in Habs Jerseys / Canadian Identity
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "Two Indian Men Danced Bhangra in Montreal Canadiens Jerseys. Canada Lost Its Mind.",
    "subheadline": "A seven-year-old video of Prateek Saini and Harshjot Singh Nijher celebrating a Habs playoff win has gone viral again — and the backlash reveals how deeply immigration anxiety has reshaped what it means to be Canadian.",
    "slug": make_slug("bhangra-habs-jerseys-canada-immigration-identity-debate"),
    "category": "news",
    "vertical": "diaspora",
    "diaspora_angle": "For the 1.8 million Indians in Canada — the country's fastest-growing immigrant group — the backlash to a joyful dance video is a reminder that cultural belonging is still conditional, even in a country that markets itself as the world's most multicultural society.",
    "tags": ["Canada", "immigration", "Bhangra", "Montreal Canadiens", "multiculturalism", "Indian diaspora", "identity", "hockey"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "American Bazaar — Bhangra in Habs jerseys: Viral video divides Canadians", "url": "https://americanbazaaronline.com/2026/05/20/bhangra-in-habs-jerseys-viral-video-divides-canadians-over-identity-and-immigration-481196/"},
        {"name": "X — original viral clip and commentary", "url": "https://x.com"}
    ]),
    "score_total": 77,
    "status": "published",
    "published_at": now,
    "body": """The video is seven years old and lasts less than a minute. Two Indian men — Prateek Saini and Harshjot Singh Nijher — dance bhangra on a sidewalk in Montreal, wearing red Canadiens jerseys, after the Habs clinched a playoff spot in 2017. They are smiling. They are celebrating. They are doing exactly what hockey fans do when their team wins, except they are doing it with Punjabi footwork instead of chest bumps.

This week, as the Montreal Canadiens advanced deep into the Eastern Conference finals, the clip resurfaced on X. And Canada, which has spent the better part of a decade arguing about what it means to be Canadian, promptly lost its collective mind.

## The Backlash

"Canada has been invaded. They couldn't even leave hockey alone. They had to put their Indian spin on it," wrote one widely shared X post that accumulated tens of thousands of views. Other comments were blunter, questioning whether immigrants who celebrate in ways that "look different" can ever truly belong to Canadian culture.

The backlash was not universal. Thousands of Canadians pushed back, pointing out the obvious irony: two men wearing Canadiens jerseys, celebrating a Canadian hockey team's victory, in a Canadian city, were being told they weren't Canadian enough. "They're literally wearing the jersey. They're celebrating OUR team. What more do you want?" read one reply that went viral in its own right.

But the volume and intensity of the anti-immigrant reaction — to a wholesome dance video — revealed something that polls and elections have been tracking for years: Canada's relationship with its own multicultural identity is under severe strain.

## The Political Backdrop

The bhangra debate did not happen in a vacuum. Canada is in the middle of its most fraught national conversation about immigration since the 1990s. Housing prices in Toronto and Vancouver have made homeownership impossible for a generation of young Canadians, and immigration — particularly from India — has become the lightning rod for that frustration.

The numbers are not abstract. India has been Canada's top source country for new permanent residents for several consecutive years. The Indian-origin population in Canada now exceeds 1.8 million, making it the country's largest visible-minority group. Temporary foreign workers and international students from India have surged into secondary cities and smaller towns, creating friction in communities that had little prior experience with large-scale immigration.

The federal government has responded by tightening temporary resident pathways and reducing immigration targets for 2026 and 2027. But the political damage — fuelled by viral videos, housing statistics, and a steady stream of online content framing immigrants as economic competitors rather than contributors — has already reshaped the discourse.

## Why a Dance Video Matters

The bhangra-in-Habs-jerseys episode is culturally significant precisely because it is trivial. The men in the video were not making a political statement. They were not demanding accommodation or special treatment. They were fans of a hockey team expressing joy in the way they knew how — which happened to include a dance form that originated in Punjab rather than Quebec.

The fact that this was enough to trigger a national argument about "invasion" and "dilution" tells a story about where the goalposts have moved. Integration, for Canada's Indian community, is no longer measured by speaking English or French, paying taxes, or cheering for the Canadiens. It is being measured by whether your celebration looks right.

For Indian-Canadians — many of whom are second or third-generation citizens — the message is disorienting. The country that recruited their parents, that issued them citizenship, that put multiculturalism in its constitution, is now debating whether their dance moves are too foreign for hockey.

## The View From the Diaspora

In Indian communities from Brampton to Surrey, the video has become a Rorschach test. Younger Indo-Canadians tend to see it as a moment of defiant joy — proof that you can love bhangra and the Habs simultaneously, and that anyone who has a problem with that is revealing their own insecurity. Older community members are more cautious, wary of backlash that could translate into policy hostility or workplace discrimination.

For NRIs in the United States, the debate is familiar but not identical. American immigration politics are equally heated, but the cultural battleground is different — assimilation in the US has always been more explicitly expected, while Canada's official multiculturalism was supposed to make room for difference. When that room starts shrinking, it rattles a foundational promise.

## What Comes Next

The Canadiens' playoff run will end eventually. The bhangra video will cycle out of the timeline. But the underlying tensions — about who belongs, what integration looks like, and whether a country built by immigrants can stay welcoming to them — are not going anywhere.

Prateek Saini and Harshjot Singh Nijher danced because their team won. That should have been the whole story. In 2026 Canada, it's just the beginning of one.""",
    "word_count": 820,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 3: NEWS — India-South Korea Defense MoUs Signed
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "India and South Korea Just Signed Three Defence Agreements in Seoul. The Iran War Is Rewriting Asia's Military Map.",
    "subheadline": "Rajnath Singh's visit produced MoUs on cybersecurity, military training, and UN peacekeeping — signalling a defence partnership that goes far beyond arms deals, at a moment when both countries face mounting pressure from a destabilised Middle East.",
    "slug": make_slug("india-south-korea-defence-mou-cybersecurity-iran-war"),
    "category": "news",
    "vertical": "geopolitics",
    "diaspora_angle": "India's deepening military ties with South Korea matter to NRIs because they shape the security architecture of the Indo-Pacific — the region where Indian and American strategic interests increasingly converge. For the growing Indian community in South Korea, the relationship also opens professional and academic pathways in defence technology.",
    "tags": ["India", "South Korea", "Rajnath Singh", "defense", "cybersecurity", "MoU", "Indo-Pacific", "Iran war", "military cooperation"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Korea JoongAng Daily — Korean, Indian defense chiefs discuss arms cooperation", "url": "https://koreajoongangdaily.joins.com"},
        {"name": "The Hindu Business Line — India eyes S Korea's military industry might", "url": "https://www.thehindubusinessline.com"},
        {"name": "Devdiscourse — India-South Korea seal strategic defence MoU on cybersecurity", "url": "https://www.devdiscourse.com"},
        {"name": "GKToday — India, South Korea Sign Defence MoU on Cybersecurity", "url": "https://gktoday.in"},
        {"name": "Indian Economic Observer — Defence cooperation agreements signed", "url": "https://indianeconomicobserver.com"}
    ]),
    "score_total": 73,
    "status": "published",
    "published_at": now,
    "body": """India's Defence Minister Rajnath Singh signed three bilateral agreements with his South Korean counterpart Ahn Gyu-back in Seoul this week, expanding a military relationship that has quietly become one of Asia's most strategically consequential — and one that the Iran war has made urgent.

The memoranda of understanding, exchanged during Singh's May 19-21 visit to the Republic of Korea, cover defence cybersecurity cooperation, training exchanges between India's National Defence College and Korea National Defence University, and a framework for UN peacekeeping collaboration. Taken individually, each agreement is incremental. Taken together, they represent a deliberate and accelerating convergence between two of Asia's largest democracies on the question of how to secure the Indo-Pacific in a world where the Middle East is on fire and the old security assumptions no longer hold.

## Why Seoul, Why Now

The timing of Singh's visit was not accidental. The Iran conflict, now in its third month, has disrupted energy supply chains that both India and South Korea depend on. South Korea imports roughly 70 per cent of its crude oil from the Middle East; India's dependence is comparable. Both countries have watched the Strait of Hormuz disruptions push fuel prices to levels that threaten domestic economic stability.

That shared vulnerability has created a common interest in building defence capacity that does not depend entirely on the United States. India's Act East Policy and South Korea's Indo-Pacific strategy have been converging for years, but the current crisis has injected a sense of operational urgency into what was previously a diplomatic formality.

"I will focus on deepening strategic military cooperation, strengthening defence industrial partnerships, and boosting maritime collaboration, promoting peace and stability in the Indo-Pacific region," Singh wrote on X ahead of the meetings.

## The Cybersecurity MoU

The most significant of the three agreements is the defence cybersecurity pact. Cyber warfare has become the fastest-growing domain of military conflict globally, and both India and South Korea face persistent threats — India from Pakistan-linked and Chinese state-sponsored groups, South Korea from North Korea's increasingly sophisticated cyber operations.

The MoU establishes a framework for information sharing, joint training exercises, and collaborative responses to cyber threats targeting military infrastructure. For India, which has been building its Defence Cyber Agency since 2018, the partnership with South Korea — one of the world's most digitally advanced militaries — offers access to capabilities and operational doctrine that would take years to develop independently.

## The Defence Industrial Angle

Beyond the signed agreements, the larger story of the visit was the deepening of defence industrial cooperation. South Korea has emerged as one of the world's top arms exporters, with companies like Hanwha Aerospace, LIG Nex1, and Korea Aerospace Industries winning major contracts across Europe, the Middle East, and Southeast Asia.

India, which remains the world's largest arms importer despite years of "Make in India" defence manufacturing initiatives, sees South Korea as a potential partner for co-production and technology transfer — particularly in areas like artillery systems, surface-to-air missiles, and naval platforms.

The bilateral talks in Seoul included discussions on expanding military-to-military ties and identifying specific defence industrial projects for joint development. While no specific contracts were announced, officials from both sides described the conversations as more substantive and operationally focused than previous rounds.

## The Indo-Pacific Chess Board

The India-South Korea defence relationship exists within a broader strategic architecture that includes the US, Japan, and Australia. While India has been careful not to formalise its partnerships into explicit alliance structures — maintaining its traditional preference for strategic autonomy — the practical reality is that its military cooperation with US-allied democracies in Asia has expanded dramatically since the Iran war began.

For South Korea, the calculus is different but complementary. Seoul's $150 billion economic agreement with Washington, which includes commitments to increase defence spending to 3.5 per cent of GDP and purchase $25 billion in US military equipment by 2030, has given it both the resources and the political cover to deepen ties with non-traditional partners like India.

## What NRIs Should Watch

For the Indian diaspora, the India-South Korea defence axis may seem distant from daily life, but its implications are concrete. A more capable Indian military — one that benefits from Korean cybersecurity expertise, joint training programmes, and co-produced weapons systems — is a more effective guarantor of the stability that sustains India's economic growth, protects trade routes, and secures the energy supplies that keep the lights on.

The agreements signed in Seoul this week are building blocks, not breakthroughs. But in a world where the Middle East is reminding everyone that security cannot be outsourced, they are the right building blocks at the right time.""",
    "word_count": 780,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# ARTICLE 4: NEWS — India Fuel Crisis: No Shortage vs. Reality
# ══════════════════════════════════════════════════════════════

articles.append({
    "id": str(uuid.uuid4()),
    "topic_id": None,
    "headline": "India Says There Is No Fuel Shortage. Truckers in Gujarat, Protesters in Bihar, and LPG Data Tell a Different Story.",
    "subheadline": "State-run oil companies insist supplies are stable. But diesel queues in Kutch, a 50 per cent collapse in LPG imports, and street protests across half a dozen states suggest the government's reassurances are running on fumes.",
    "slug": make_slug("india-fuel-shortage-lpg-crisis-government-denials-reality"),
    "category": "news",
    "vertical": "economy",
    "diaspora_angle": "For NRIs sending money home to families that depend on LPG for cooking and diesel for livelihoods, the gap between official reassurances and ground reality is not academic — it determines whether that money is enough. When India's energy supply cracks, the cost is paid in kitchens and truck stops, not in parliament.",
    "tags": ["India", "fuel shortage", "diesel", "LPG", "Iran war", "Strait of Hormuz", "IOCL", "BPCL", "HPCL", "Gujarat", "Bihar"],
    "urgency": "developing",
    "sources": json.dumps([
        {"name": "The Hindu Business Line — LPG disruption pushes India's March petroleum imports to 8-year low", "url": "https://www.thehindubusinessline.com"},
        {"name": "India Shipping News — Transport body seeks urgent action in Gujarat amid diesel shortage", "url": "https://indiashippingnews.com"},
        {"name": "LatestLY — Oil companies assure uninterrupted fuel supply", "url": "https://www.latestly.com"},
        {"name": "NationPress — No petrol, diesel or LPG shortage, govt confirms", "url": "https://nationpress.com"},
        {"name": "IEA — India's LPG imports affected by Gulf conflict", "url": "https://www.iea.org"}
    ]),
    "score_total": 80,
    "status": "published",
    "published_at": now,
    "body": """The Indian government would like you to know that there is no fuel shortage. State-run oil marketing companies — Indian Oil Corporation, Bharat Petroleum, and Hindustan Petroleum — have issued statements confirming that petrol, diesel, and LPG supplies remain "stable" and "uninterrupted" across the country. Officials have emphasised that any localised disruptions are the result of seasonal demand patterns and consumer migration from private to public-sector fuel stations, not systemic supply failures.

The truckers in Gujarat would like you to know something different.

## What the Ground Looks Like

The Akhil Gujarat Truck Transport Association issued an urgent appeal this week, warning of severe diesel shortages in Kutch, Saurashtra, and North Gujarat that have disrupted logistics and trade across the state. Transporters report that retail fuel stations in these regions are rationing diesel, forcing truckers to queue for hours or drive dozens of kilometres to find a pump with supply. Some have resorted to purchasing diesel at premium prices from unauthorised sources — a practice that is both illegal and a reliable indicator that official channels are failing.

In Uttar Pradesh, Bihar, Rajasthan, Maharashtra, and Haryana, street protests have broken out over fuel prices and availability. Videos circulating on social media show long queues at petrol pumps, angry crowds confronting station managers, and opposition politicians — led by Rahul Gandhi and Akhilesh Yadav — accusing the Modi government of prioritising optics over energy security.

Meanwhile, the data tells its own story. India's petroleum imports in March fell to an eight-year low, according to The Hindu Business Line, driven primarily by a collapse in LPG inflows. The International Energy Agency reported that India's LPG imports dropped by more than half over March and April 2026 — a loss of approximately 430,000 barrels per day — as the Iran conflict disrupted Gulf supply chains.

## The Strait of Hormuz Problem

The root cause is not domestic mismanagement but geopolitics. The Iran war, now in its third month, has intermittently disrupted traffic through the Strait of Hormuz, the narrow waterway through which roughly 20 per cent of the world's oil supply and a significant share of global LPG flows. India, which imports over 80 per cent of its crude oil, is acutely vulnerable to any disruption in Gulf supply routes.

The government's response has been to diversify sourcing — increasing purchases from Russia, the United States, and West Africa — and to draw down strategic petroleum reserves. These measures have prevented a full-blown crisis on the scale of the 1990 Gulf War disruption, but they have not been sufficient to eliminate shortages in regions that sit at the end of India's domestic distribution chain.

The ₹3.91 per litre price increase announced in May — described by officials as "the world's smallest among major economies" — was an acknowledgement that costs were rising faster than the government's ability to subsidise them. But for truckers, farmers, and households that depend on affordable fuel, the distinction between "the world's smallest price hike" and "a price hike that breaks the monthly budget" is not comforting.

## The LPG Alarm

The LPG situation deserves particular attention. India's cooking gas programme — Ujjwala Yojana — was one of the Modi government's signature welfare achievements, providing subsidised LPG connections to over 90 million households. The programme's success depends entirely on reliable supply. When imports collapse by 50 per cent, the downstream impact is not measured in barrels but in kitchens — in families that cannot cook a meal because the cylinder delivery has been delayed by weeks.

Maharashtra's food and civil supplies minister, Chhagan Bhujbal, warned this week of potential LPG service disruptions by June 30 if international supply chains are not restored. The statement was notable for its specificity: a sitting state minister putting a date on a crisis that the central government insists does not exist.

## The Gap Between Statement and Street

India has a long tradition of official reassurance that runs ahead of — or sideways to — ground reality. The OMCs' statements that supplies are "stable" may be technically accurate at the national level: India is not running out of fuel. Strategic reserves are not depleted. Refineries are operating. The problem is distribution — the last mile of a supply chain that stretches from Gulf loading terminals to rural diesel pumps in Kutch.

For NRIs whose families depend on LPG deliveries and diesel-powered livelihoods, the official "no shortage" messaging is increasingly difficult to reconcile with what their relatives are reporting. When your mother in Patna says the LPG cylinder is three weeks late and the government says supply is stable, someone is wrong — and it is usually not your mother.

## What Happens Next

The trajectory depends almost entirely on the Iran conflict. A ceasefire or de-escalation that reopens the Strait of Hormuz would relieve pressure within weeks. A prolonged conflict — or an escalation that further disrupts Gulf logistics — would push India's energy system closer to a breaking point that no amount of official reassurance can paper over.

The monsoon season, which begins in June, will compound the problem. Agricultural diesel demand peaks during planting, and LPG demand remains constant regardless of weather. If imports do not recover by July, the gap between what the government says and what the country experiences will become impossible to ignore.""",
    "word_count": 870,
    "image_url": None,
    "image_attribution": None,
    "image_caption": None,
    "gallery_images": None,
})

# ══════════════════════════════════════════════════════════════
# INSERT ALL ARTICLES
# ══════════════════════════════════════════════════════════════

print(f"Inserting {len(articles)} articles...")
success = 0
for i, article in enumerate(articles):
    try:
        result = sb_post("p2_articles", article)
        if isinstance(result, list) and len(result) > 0:
            print(f"  ✅ [{article['category']}] {article['headline'][:80]}...")
            success += 1
        elif isinstance(result, dict) and result.get("id"):
            print(f"  ✅ [{article['category']}] {article['headline'][:80]}...")
            success += 1
        else:
            print(f"  ⚠️  [{article['category']}] Response: {json.dumps(result)[:200]}")
    except requests.exceptions.HTTPError as e:
        print(f"  ❌ [{article['category']}] Error: {e}")
        print(f"     Response: {e.response.text[:300]}")
    except Exception as e:
        print(f"  ❌ [{article['category']}] Error: {e}")

print(f"\nDone: {success}/{len(articles)} articles published.")
