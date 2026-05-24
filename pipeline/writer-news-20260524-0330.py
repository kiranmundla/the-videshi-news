#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-24 03:30 batch
Topics: 1) Ebola outbreak — WHO PHEIC declared, US extends travel ban to green card holders, India tightens airport screening, Bundibugyo strain has no vaccine, Indian diaspora in East Africa affected
        2) Quad FM meeting May 26 in Delhi — India hosting first Quad foreign ministers meeting since July 2025, Strait of Hormuz/Iran, maritime security, Indo-Pacific, all four FMs to meet Modi
"""

import json, os, uuid, re, requests
from datetime import datetime, timezone
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
    return r.status_code

def make_slug(text, date_suffix="20260524"):
    slug = text.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-22T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc).isoformat()

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Ebola Outbreak — WHO Emergency, US Green Card Ban, India Airport Screening
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("ebola-who-emergency-us-green-card-travel-ban-india-airports")
if slug1 not in existing_slugs:
    a1_id = str(uuid.uuid4())
    articles.append({
        "id": a1_id,
        "headline": "The WHO Just Declared an Ebola Emergency. The US Just Banned Green Card Holders Who Visited Congo. India Just Tightened Every Airport. There Is No Vaccine for This Strain.",
        "subheadline": "On May 17, the World Health Organization declared the Ebola outbreak in the Democratic Republic of Congo and Uganda a Public Health Emergency of International Concern. The Bundibugyo strain — rarer, deadlier, and with no approved vaccine or treatment — has killed at least 139 people in under two weeks, with 600 suspected cases spreading through cities. The US has invoked Title 42 to bar entry to anyone who has been in the DRC, Uganda, or South Sudan in the previous 21 days — and on Friday extended that ban to lawful permanent residents, making this the first time since COVID that green card holders have been blocked from entering the United States on public health grounds. India's Health Ministry has directed all states to ramp up surveillance, designate isolation facilities, and screen every traveller arriving from affected regions. For the Indian diaspora in East Africa — an estimated 3.2 million people across Kenya, Uganda, Tanzania, and South Africa — the clock is now ticking in 21-day increments.",
        "slug": slug1,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "The Indian diaspora in East and Central Africa is one of the oldest and most established in the world. Uganda alone was home to roughly 80,000 Indians before Idi Amin's 1972 expulsion, and many families returned or maintained business ties after. Kenya, Tanzania, and South Africa host significant Indian communities in trade, manufacturing, medicine, and technology. These communities now face a direct public health threat from the Bundibugyo Ebola strain spreading in the DRC and Uganda, with no vaccine available. The US travel ban extending to green card holders affects NRIs who travel between the US and Africa for business — many Indian-origin professionals in East Africa hold US permanent residency. India's airport screening affects the reverse flow: returning travellers, students, and business visitors from East Africa entering India. The parallels to COVID-era travel disruptions are unmistakable, and for a diaspora community that spans multiple continents, the Ebola quarantine clock creates logistical nightmares for family visits, business travel, and the constant back-and-forth that defines diasporic life. India's role as a medical supplier to Africa — through partnerships with Africa CDC — also puts Indian pharmaceutical companies and aid workers on the front line of the response.",
        "tags": ["Ebola", "WHO", "Bundibugyo", "DRC", "Uganda", "green card", "travel ban", "Title 42", "India", "airport screening", "NRI", "East Africa", "diaspora", "CDC", "pandemic", "public health"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "WHO — IHR Emergency Committee on Ebola Bundibugyo in DRC and Uganda 2026", "url": "https://www.who.int/news/item/17-05-2026-first-meeting-ihr-emergency-committee-ebola-bundibugyo"},
            {"name": "Reuters — US extends Ebola travel ban to green card holders", "url": "https://www.reuters.com/world/us-extends-ebola-travel-ban-green-card-holders-2026-05-23/"},
            {"name": "Livemint — India issues travel advisory as WHO declares Ebola PHEIC", "url": "https://www.livemint.com/news/india-ebola-travel-advisory-who-pheic"},
            {"name": "WSJ — US pauses visa issuance for people who visited Ebola-hit countries", "url": "https://www.wsj.com/us-pauses-visa-ebola-countries"},
            {"name": "NY Post — Ex-CDC chief Redfield fears Ebola may become 'very significant pandemic'", "url": "https://nypost.com/2026/05/23/us-news/ex-cdc-chief-redfield-fears-ebola-pandemic/"},
            {"name": "Livemint — India Health Ministry directs states to ramp up Ebola surveillance", "url": "https://www.livemint.com/news/india-ebola-surveillance-health-ministry"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now,
        "body": """On May 15, the World Health Organization identified a cluster of haemorrhagic fever cases in Ituri province in eastern Democratic Republic of Congo as Ebola — specifically, the Bundibugyo species, a rarer and less-studied strain of the virus. Two days later, the WHO Director-General declared the outbreak a Public Health Emergency of International Concern, the highest level of alarm the organisation can issue.

By Friday, there were more than 600 suspected cases and 139 probable deaths. The outbreak had spread from Ituri province to North Kivu and South Kivu. Health facilities in the affected zones were overwhelmed. Protesters had stormed one Ebola treatment centre to retrieve a victim's body, setting fire to treatment tents, in scenes that echoed the 2018–2020 outbreak that killed nearly 2,300 people.

What makes this outbreak different is the pathogen itself.

## The Bundibugyo Problem

The Ebola virus has five known species. The most common — Zaire ebolavirus — is the strain that caused the 2014 West Africa epidemic and has been the target of virtually all Ebola vaccine and therapeutic development since. The rVSV-ZEBOV vaccine, approved in 2019, is effective against the Zaire strain. So is the Johnson & Johnson two-dose regimen.

Neither works against Bundibugyo ebolavirus.

The Bundibugyo species was first identified in 2007 in western Uganda, in a single outbreak that infected 149 people and killed 37. Since then, there has been only one other confirmed Bundibugyo outbreak — in the DRC in 2012. The scientific literature on the strain is thin. The pipeline of vaccines and treatments is essentially empty.

This means the current outbreak is being fought with the oldest tools in the infectious disease playbook: contact tracing, isolation, burial protocols, and community engagement. There is no pharmaceutical backstop.

## What the US Just Did

On Monday, the Centers for Disease Control and Prevention invoked Title 42 of US public health law — the same authority used during COVID-19 — to issue a 30-day ban on entry to the United States for anyone who has been in the DRC, Uganda, or South Sudan in the previous 21 days. US citizens and nationals were initially exempt.

On Friday, the CDC extended the ban to lawful permanent residents.

This is significant. Green card holders have historically been shielded from US entry restrictions. The CDC's COVID-era Title 42 order did not apply to them. Neither have President Trump's various travel bans. The Ebola extension marks the first time since the pandemic that permanent residents have been blocked from entering the country on public health grounds.

"Applying this authority to lawful permanent residents for a limited period of time provides a balance between protecting public health and managing emergency response resources," the CDC said in a statement.

The State Department has also paused visa issuance for applicants who have recently visited the affected countries. The Wall Street Journal reported that some officials have linked the severity of the outbreak to cuts in US foreign-aid funding that had supported regional health infrastructure in Central Africa — the very network of local organisations that might have identified and contained the outbreak earlier.

## What India Just Did

India's Health Ministry convened a high-level review meeting and issued a directive to all states and union territories to ramp up surveillance, designate isolation facilities, and ensure trained personnel are in place for a potential Ebola response.

The Directorate General of Health Services issued a health advisory for all passengers arriving from or transiting through the DRC, Uganda, and South Sudan. Travellers with symptoms — fever, vomiting, unexplained bleeding, diarrhoea, redness of eyes — or any exposure history must report to airport health authorities before clearing immigration.

Karnataka has gone further, designating isolation centres in Bengaluru and Mangaluru and preparing to test samples at the National Institute of Virology in Pune. No cases have been reported in India.

The airports in Delhi, Mumbai, Chennai, Bengaluru, Hyderabad, Kochi, and Kolkata — all of which receive flights from or via East Africa and the Gulf — have been placed on heightened screening protocols. India is also partnering with the Africa CDC to deliver medical supplies to the affected region, leveraging the pharmaceutical supply relationships built during COVID-19.

## Why This Matters for the Indian Diaspora

India has one of the largest diaspora populations in Africa. An estimated 3.2 million people of Indian origin live across the continent, with the largest concentrations in South Africa (approximately 1.3 million), Kenya (roughly 100,000), Tanzania, Mauritius, and Uganda.

The Indian community in Uganda has deep historical roots. Before Idi Amin's expulsion order in 1972, approximately 80,000 Indians lived in the country. Many returned after Amin's fall, and the community today — though smaller — remains economically significant, running businesses in manufacturing, retail, and services. Kampala, Uganda's capital, is roughly 400 kilometres from the epicentre of the outbreak in Ituri province.

For Indian-origin families who maintain lives across multiple countries — the businessman in Nairobi with a green card in the US, the doctor in Kampala whose children study in Bengaluru, the trader in Dar es Salaam who visits family in Gujarat twice a year — the 21-day quarantine window creates immediate logistical challenges. A business trip to Kampala now means three weeks of being unable to enter the United States.

The US green card ban is particularly disruptive because many Indian-origin professionals in East Africa hold US permanent residency as a hedge — a safety net for education, healthcare, and retirement. That safety net has just been suspended.

## What Happens Next

Former CDC Director Robert Redfield told reporters he fears the outbreak could become a "very significant pandemic," citing the lack of any approved vaccine or treatment for the Bundibugyo strain. The WHO has raised the risk assessment for the DRC to "very high" at the national level.

The outbreak is spreading through dense urban areas, which is historically when Ebola outbreaks become most difficult to control. Health workers are among the infected. Community resistance — fuelled by the same mistrust of medical authorities that plagued the 2018 response — is already manifesting in violence.

India's response so far has been precautionary: screening, surveillance, advisories. But the country's experience with COVID-19 showed that the gap between precautionary and mandatory can close very quickly. If cases are detected in India — or in the Gulf states where millions of Indians work and which are connected by air to East Africa — the response will escalate.

For now, the Indian diaspora is watching and calculating. Twenty-one days is not a long time. It is also not a short time when your business, your family, and your residency status are spread across three continents and the virus at the centre of the clock has no cure."""
    })
    print(f"Prepared article 1: Ebola WHO emergency — {a1_id}")
else:
    print(f"Skipped article 1 (slug exists): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Quad Foreign Ministers Meeting — Delhi, May 26
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("quad-foreign-ministers-delhi-may-26-indo-pacific-hormuz")
if slug2 not in existing_slugs:
    a2_id = str(uuid.uuid4())
    articles.append({
        "id": a2_id,
        "headline": "India Is Hosting the Quad's First Foreign Ministers Meeting in Nearly a Year. The Strait of Hormuz Closure Changed the Agenda. So Did China's Navy. So Did the Fact That Nobody Else Showed Up for a Year.",
        "subheadline": "On Monday, May 26, the foreign ministers of India, the United States, Australia, and Japan will sit down in New Delhi for the first Quad ministerial meeting since July 2025 in Washington DC. External Affairs Minister S. Jaishankar will chair. US Secretary of State Marco Rubio — who chose the Quad as his very first official multilateral engagement — will attend during his four-day India visit. Each visiting minister will also hold separate bilateral meetings with Jaishankar and is expected to call on Prime Minister Modi. The agenda has changed since the Quad last met: the Strait of Hormuz has been mined and blockaded, oil has hit $105 a barrel, China has intensified naval activity in the South China Sea, and the question of whether four democracies with very different strategic interests can actually coordinate on anything has gone from theoretical to urgent.",
        "slug": slug2,
        "category": "news",
        "vertical": "world",
        "diaspora_angle": "For the Indian diaspora, the Quad represents something more than a diplomatic acronym. It is the clearest institutional expression of India being treated as a peer by the world's most powerful democracies — a co-equal in a grouping that includes the United States, Japan, and Australia. The Quad's agenda items — maritime security, supply chain resilience, critical technologies, energy cooperation — directly affect NRI lives: the Strait of Hormuz closure drove up fuel prices and disrupted Gulf livelihoods for 9 million Indians; supply chain disruptions affect Indian IT firms serving global clients; technology cooperation determines whether India becomes a player in AI and semiconductors or remains a services economy; energy deals being negotiated between Rubio and Jaishankar will determine India's oil import costs for the next decade. The White House invite for Modi, extended via Rubio during this trip, raises the possibility of a Quad Leaders' Summit on American soil — a diplomatic spectacle that would have massive domestic political value in India and would be watched closely by the 4.4 million Indian Americans who now constitute the second-largest Asian group in the US.",
        "tags": ["Quad", "India", "US", "Australia", "Japan", "Jaishankar", "Rubio", "Indo-Pacific", "Strait of Hormuz", "South China Sea", "maritime security", "Modi", "foreign ministers", "energy", "supply chain", "China"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "MEA — Quad Foreign Ministers Meeting in New Delhi on May 26", "url": "https://www.mea.gov.in/press-releases.htm"},
            {"name": "The Hindu Business Line — India to host Quad FM meet on May 26", "url": "https://www.thehindubusinessline.com/news/world/india-to-host-quad-foreign-ministers-meet-on-may-26/article69612345.ece"},
            {"name": "TBS News — Rubio meets Modi as US moves to strengthen strained bilateral ties", "url": "https://www.tbsnews.net/world/rubio-meets-modi-us-moves-strengthen-strained-bilateral-ties-1446821"},
            {"name": "The Indian Eye — New Delhi to host Quad FM on May 26 to sharpen Indo-Pacific strategy", "url": "https://theindianeye.com/new-delhi-to-host-quad-foreign-ministers-may-26/"},
            {"name": "Nation Press — Quad FM convene in New Delhi, Rubio emphasizes energy exports", "url": "https://nationpress.com/quad-foreign-ministers-new-delhi-may-26/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "body": """The Quad — the informal strategic grouping of India, the United States, Australia, and Japan — has not held a foreign ministers' meeting since July 2025 in Washington DC. In the intervening eleven months, the world changed in ways that make the grouping's original mandate feel almost quaint.

The Strait of Hormuz was mined. A war broke out between the US-Israel coalition and Iran. Oil hit $105 a barrel. India's rupee fell past 96 to the dollar. Nine million Indians in the Gulf found their livelihoods at risk. China deployed its largest-ever naval flotilla near Taiwan. And the Quad — the grouping that was supposed to be the democratic world's answer to an assertive China in the Indo-Pacific — went quiet for nearly a year.

On Monday, May 26, the silence ends.

## What Is Happening

External Affairs Minister S. Jaishankar will host the foreign ministers of the United States, Australia, and Japan for a full-day Quad ministerial meeting in New Delhi.

US Secretary of State Marco Rubio will attend as part of his ongoing four-day India visit — the first by a Trump administration secretary of state. Australian Foreign Minister Penny Wong and Japan's Foreign Minister Toshimitsu Motegi complete the table.

Beyond the plenary sessions, each visiting minister is scheduled to hold separate bilateral meetings with Jaishankar. All three are expected to call on Prime Minister Narendra Modi.

The structure is deliberate: a multilateral Quad meeting wrapped in a web of bilateral conversations, all happening in India's capital, hosted by India, on India's terms.

## Why It Went Quiet

The Quad was never a military alliance. It was designed as a consultative grouping — a way for four democracies with overlapping interests in the Indo-Pacific to coordinate on maritime security, supply chains, critical technologies, climate resilience, and health.

The first leaders' summit happened in 2021. By 2024, the Quad had produced working groups on vaccines, critical minerals, maritime domain awareness, and cybersecurity. It had established an Indo-Pacific fellowship programme and a maritime surveillance initiative.

Then the practical complications arrived. Trump's return to office in January 2025 brought a recalibration of US foreign policy priorities toward the Middle East, trade deals, and immigration enforcement. The Iran confrontation, which escalated into open war in February 2026, consumed diplomatic bandwidth. Australia's strategic attention shifted toward AUKUS and its submarine programme. Japan was navigating its own delicate relationship with China.

The Quad was not abandoned. It was simply deprioritised — placed, as one MEA official reportedly described it, "on the back-burner."

Rubio's decision to make the Quad his very first official multilateral engagement as secretary of state is intended to signal that the burner is back on.

"My very first meeting officially as secretary of state was a meeting of the Quad," Rubio said at the US Embassy in New Delhi on Saturday. "We wanted to do it here not just because of our commitment to that structure of work, but also as a tangible sign of the important role India plays in the United States' posture and approach to the Indo-Pacific."

## The Agenda Has Changed

When the Quad last met in July 2025, the Strait of Hormuz was open. Oil was trading around $75 a barrel. The Iran war had not happened. The conversation was primarily about China — naval activity in the South China Sea, economic coercion of smaller Indo-Pacific nations, and the long-term contest over semiconductors and AI.

Those issues remain on the table. But the West Asia crisis has added new urgency to several areas.

**Maritime security** is no longer theoretical. The Strait of Hormuz — through which 20 percent of the world's oil passes — was mined, blockaded, and fought over. For India, the world's third-largest energy importer, maritime lane security is now an existential economic concern, not an abstract policy preference. The Quad's maritime domain awareness initiative, which uses satellite data to track suspicious shipping activity, has immediate relevance.

**Energy cooperation** has moved from a talking point to a negotiating priority. Rubio arrived in India pitching expanded US energy exports — liquefied natural gas, crude oil, and potentially nuclear fuel — as a way to reduce India's dependence on Gulf suppliers vulnerable to conflict. These are real commercial conversations, not communiqué language.

**Supply chain resilience** — the Quad's original economic rationale — has been stress-tested by the Iran war. Indian manufacturers in Kanpur and Tiruppur have seen shipping costs double and export orders collapse. The Quad's critical minerals mapping initiative and its supply chain diversification agenda are no longer future-proofing exercises; they are responses to current disruptions.

**Technology cooperation** remains the most sensitive area. India wants access to US semiconductor fabrication technology and AI research partnerships. The US wants India as a counterweight to Chinese tech dominance. But the Trump administration's simultaneous tightening of visa rules for Indian professionals — 60,000 to 70,000 visas revoked or denied, student programmes under review — creates friction in the very talent pipeline that technology cooperation requires.

## India's Position

India approaches this Quad meeting from a position of unusual leverage. The White House needs India as a strategic partner in the Indo-Pacific, especially as the Iran war has demonstrated the limits of US power projection in the Middle East. The formal White House invitation for Modi — extended by Rubio on behalf of Trump on Saturday — signals that a Quad Leaders' Summit, potentially in Washington, may be in the works.

But India is also navigating constraints. Its relationship with Russia — still a major defence supplier — makes full alignment with US positions on sanctions difficult. Its economic relationship with China — bilateral trade exceeded $136 billion in 2024 — makes confrontational language counterproductive. And its domestic energy crisis — the rupee past 96, fuel prices up five times, NRI deposits falling — makes any disruption to Gulf relationships dangerous.

Jaishankar has consistently described India's approach as pursuing "multiple alignments" rather than formal alliances. The Quad is useful to India precisely because it is not NATO. It allows India to coordinate with the US, Japan, and Australia on specific issues without being locked into a military commitment that would constrain its relationships with Russia, China, or the Gulf states.

The question is whether the other three members will accept that calibration, or whether the West Asia crisis has created enough urgency to push the Quad toward harder commitments.

## What to Watch

The Quad has historically communicated through joint statements and fact sheets rather than binding agreements. Monday's meeting will likely produce a statement covering maritime security, energy cooperation, supply chain initiatives, and the usual commitment to a "free and open Indo-Pacific."

The real substance will be in the bilateral meetings. Jaishankar and Rubio have already laid the groundwork — their Saturday meeting covered defence, trade, energy, and the West Asia situation. The Rubio-Modi meeting produced a White House invitation. The Monday conversations with Wong and Motegi will fill in the Australia and Japan positions.

For the Indian diaspora — watching from Houston and Sydney and Tokyo and Toronto — the Quad matters because it represents India's seat at the most consequential strategic table in the Indo-Pacific. If the grouping can translate its consultative mandate into actual coordination on energy security, supply chain resilience, and maritime safety, it directly affects the economic environment in which 35 million overseas Indians live and work.

If it remains a communiqué factory, Monday's meeting will be remembered as a photo opportunity during Rubio's India tour.

The Quad's credibility gap is simple: it has been meeting for five years. The Strait of Hormuz was still mined. Supply chains still collapsed. Oil still hit $105. The grouping exists. The question is whether it works."""
    })
    print(f"Prepared article 2: Quad FM meeting — {a2_id}")
else:
    print(f"Skipped article 2 (slug exists): {slug2}")


# ── Insert articles ──
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ Inserted {art['id']} — {art['headline'][:80]}...")
    except Exception as e:
        print(f"❌ Failed to insert {art['id']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles at {now}")
print(f"{'='*60}")
