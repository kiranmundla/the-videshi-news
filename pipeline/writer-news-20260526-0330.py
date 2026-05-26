#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~03:30 PDT batch
Topics: 1) Pentagon vs SpaceX over Starlink price hike during Iran war — $5K to $25K per terminal, $500M for direct-to-cell, military dependence on Musk, SpaceX IPO leverage
        2) India-Bangladesh border pushbacks — India pushing hundreds of "declared foreigners" into Bangladesh, border patrols intensified, Supreme Court orders Centre to bring some back
"""

import json, os, uuid, re, requests, subprocess, urllib.parse
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

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Wikipedia person image (MANDATORY for person articles) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "100"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: Pentagon vs SpaceX — Starlink Price Hike During Iran War
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("pentagon-spacex-starlink-price-hike-iran-war-25000-terminal")
if slug1 not in existing_slugs and not any("pentagon" in h and "spacex" in h for h in existing_headlines_lower) and not any("starlink" in h and "price" in h for h in existing_headlines_lower):
    body1 = """As American kamikaze drones guided by Elon Musk's Starlink satellite network began striking Iranian military targets with increasing accuracy, senior SpaceX officials reached a business conclusion: The Pentagon should be paying more.

Within weeks of the United States launching its bombing campaign on February 28, SpaceX executives met Pentagon officials and argued the military had been paying about $5,000 per terminal while effectively using a higher tier of service worth closer to $25,000 per month. The Pentagon, which was ramping up strikes on Iran, ultimately agreed to pay the increase — nearly doubling the cost of each LUCAS suicide drone from approximately $30,000 to $55,000.

This is the story of how one company gained so much leverage over the world's most powerful military that it could raise prices during a war — and the Pentagon had no choice but to pay.

## The Price of Monopoly

The LUCAS drone is America's answer to Iran's Shahed. It is cheap, disposable, and effective. It circles over a target area, identifies the objective, and dives to detonate on impact. What makes it work is Starlink — the satellite internet connection that allows it to be guided with precision from thousands of miles away.

SpaceX argued that the LUCAS drones were operating under conditions that aligned more closely with its aviation-tier subscription rather than the lower-priced land or mobility service the Pentagon had been purchasing. Pentagon officials countered that the $25,000 monthly price tag was designed for manned aircraft, not expendable drones that used a Starlink connection for a matter of minutes or hours before destroying themselves.

The Pentagon's argument was straightforward: why should a drone that connects for ninety minutes before flying into a building pay the same monthly rate as a passenger jet that uses the service continuously? SpaceX's argument was equally simple: the service tier is defined by the capability provided, not the duration of use.

SpaceX won.

It won because there is no alternative. SpaceX's constellation of roughly 10,000 satellites accounts for more than 60 percent of all satellites in orbit. OneWeb and Amazon's Project Kuiper are building competing constellations, but neither offers a comparable military-grade service. The Pentagon's Commercial Satellite Communications Office told Reuters it is "working to find other competitors." But there are none that can do what Starlink does, at the scale Starlink does it, right now.

Clayton Swope, a senior fellow at the Center for Strategic and International Studies, did not mince words: SpaceX "certainly has the U.S. government over the barrel."

## $500 Million to Help Iranians Get Online

The pricing dispute extends beyond drones.

After Iran's government cracked down on protests in January — killing thousands of people — the Trump administration smuggled more than 6,000 Starlink terminals into Iran to provide internet access to citizens during the government-imposed blackout. As the war intensified, Iranian authorities confiscated many of the terminals and deployed jamming devices across major cities to disrupt the remaining connections.

Within a week of the conflict beginning, Pentagon officials began discussions with SpaceX about deploying direct-to-cell service — a capability similar to 5G that would allow Iranian citizens to connect to the internet using their phones without needing a ground terminal. The technology bypasses jamming and confiscation because the signal comes directly from satellites to handsets.

SpaceX's proposed price: $500 million to launch the capability, plus $100 million per month to operate it.

The Pentagon's reaction, according to sources familiar with the discussions, was alarm. The price dwarfed what defense officials had budgeted for Iranian communications operations. Reuters could not determine whether an agreement has been reached.

For context, $500 million is roughly the annual budget of the Pentagon's entire counter-communications division. $100 million per month is $1.2 billion per year — more than the United States spends on the entire International Space Station annually.

## The Ukraine Precedent

This is not the first time SpaceX's leverage over military operations has caused concern.

During the Ukraine war in 2022, Elon Musk ordered Starlink service switched off in parts of the country as Ukrainian forces advanced on Russian positions in Crimea, disrupting a key counteroffensive. The decision was made unilaterally by the CEO of a private company, without consultation with the Pentagon or the Ukrainian military. Musk later said he feared the offensive could trigger a nuclear response from Russia.

More recently, last summer, a global Starlink outage cut off connections to unmanned U.S. Navy boats during testing, leaving them bobbing in the ocean with no ability to communicate or navigate. The incident prompted classified reviews within the Pentagon about the risks of single-vendor dependence for critical military infrastructure.

The Iran war has brought these concerns to a head. At the outset of the conflict, Starshield terminals — the military-specific version of Starlink — were being used across more than a dozen drone systems. Starlink has become not just a communications tool but a targeting system, a guidance platform, and a battlefield awareness network. When SpaceX raises prices, the Pentagon does not just pay more for internet — it pays more for the ability to wage war.

On March 1 — one day after the bombing campaign began — Musk posted on X that it is "a violation of commercial Starlink terms of service to use the terminal for weapon systems." He distinguished between commercial Starlink and the government-operated Starshield network, but the post underscored an uncomfortable reality: the line between Musk's commercial empire and America's military capability is blurring in ways that neither institution fully controls.

## The IPO Connection

The timing of SpaceX's price demands is not incidental. The company is preparing for an initial public offering next month that could be among the largest in history, with a valuation estimated at $1.75 trillion. SpaceX generated $11.4 billion in revenue from Starlink alone in 2025.

Maximizing revenue from the Pentagon is one way to show potential investors that Starlink's government business — which accounts for approximately 20 percent of SpaceX's total revenue — is growing. A deal to provide direct-to-cell service in Iran at $100 million per month would represent a significant new revenue stream.

The Pentagon is currently considering an additional purchase of more than 3,500 Starshield terminal subscriptions, including 100 with the higher-priced aviation tier. The deal could generate hundreds of millions of dollars in annual revenue for SpaceX.

The government, in other words, is about to become an even larger customer of a company that is simultaneously preparing to go public and raising prices on the government. The conflict of interest is not hypothetical — it is the business model.

## What India Is Watching

India's defense establishment has been paying close attention to the SpaceX-Pentagon dynamic for one reason: it does not want to be in the same position.

India's military modernization plan, which envisions $130 billion in defense spending over the next five years, includes significant investments in satellite communications, drone warfare, and precision targeting — exactly the capabilities that the Pentagon now depends on SpaceX to provide. India is building its own satellite constellation through ISRO's commercial arm, NewSpace India Limited (NSIL), but the program is years behind SpaceX in both scale and capability.

The Starlink pricing dispute validates India's insistence on indigenous defense technology development. DRDO's Medium Altitude Long Endurance (MALE) drone program, the Tapas BH-201, uses Indian-built satellite links rather than commercial foreign providers. The Indian Navy's Advanced Light Helicopter fleet communicates through ISRO's GSAT satellites. These systems are less capable than their SpaceX-dependent American counterparts — but they cannot be switched off by a billionaire in Texas.

The Quad Foreign Ministers' Meeting in Delhi on Monday, which signed critical minerals and rare earths agreements between India and the US, did not address satellite communications dependency. But Indian defense officials have privately raised concerns about the growing American military dependence on SpaceX — particularly as India expands joint exercises, intelligence sharing, and interoperability with U.S. forces under the BECA and LEMOA agreements.

If India's military is going to operate alongside American forces, the question of what happens when SpaceX raises prices or Musk tweets about terms of service violations is not abstract. It is operational.

## What NRIs Are Watching

For the Indian diaspora in tech — the 300,000 Indians working in Silicon Valley, the engineers at SpaceX's competitors, the investors watching the IPO — the Pentagon-SpaceX standoff is a case study in what happens when a single company becomes too important to negotiate with.

Many NRIs will recognize the pattern. In the enterprise software world, vendor lock-in is a known risk: you build your systems on one provider's platform, and then that provider raises prices because switching costs are prohibitive. The Pentagon is experiencing vendor lock-in at the scale of national security.

The SpaceX IPO will be the most-watched financial event of 2026. Indian-origin investors and tech professionals will be among its largest individual buyer cohorts, based on demographic patterns from previous tech IPOs. They will be buying into a company that has the world's most powerful military as a captive customer — and that has demonstrated its willingness to raise prices during a war.

That is, depending on your perspective, either the best investment thesis in a generation or the clearest warning sign that one man has too much power over one country's military. For most NRI investors, it will probably be both."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "SpaceX Raised Starlink Prices on the Pentagon During a War. The Military Had No Choice but to Pay. Each Kamikaze Drone Now Costs Nearly Double. Direct-to-Cell Service in Iran Was Quoted at $500 Million Plus $100 Million a Month.",
        "subheadline": "Within weeks of the U.S. launching its bombing campaign against Iran, SpaceX told the Pentagon it was underpaying for Starlink — $5,000 per terminal when the service was 'worth' $25,000. The Pentagon agreed. Each LUCAS suicide drone went from $30,000 to $55,000. SpaceX also quoted $500 million upfront plus $100 million per month to provide direct-to-cell internet to Iranian citizens during the blackout. No competitor can match Starlink's 10,000-satellite constellation. India's defense establishment is watching — and building alternatives.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For the 300,000 Indians in Silicon Valley and NRI tech investors globally, the Pentagon-SpaceX standoff is vendor lock-in at national security scale — a pattern every enterprise software engineer recognizes. The SpaceX IPO next month will be the most-watched financial event of 2026, and Indian-origin investors will be among its largest individual buyer cohorts. They will be buying into a company that has the Pentagon as a captive customer and has demonstrated willingness to raise prices during a war. India's defense establishment is building alternatives through ISRO/NSIL to avoid the same dependency — but as India deepens military interoperability with the US under BECA and LEMOA, SpaceX's leverage becomes India's problem too.",
        "tags": ["SpaceX", "Starlink", "Pentagon", "Iran war", "Elon Musk", "LUCAS drone", "Starshield", "military", "satellite", "price hike", "IPO", "ISRO", "India defense", "vendor lock-in", "NRI", "Silicon Valley"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Pentagon spars with SpaceX over Starlink price hike during Iran war", "url": "https://www.reuters.com/business/aerospace-defense/pentagon-spars-with-spacex-over-starlink-price-hike-during-iran-war-2026-05-26/"},
            {"name": "CSIS — SpaceX and National Security: The Risks of Single-Vendor Dependence", "url": "https://www.csis.org/analysis/spacex-national-security"},
            {"name": "Reuters — SpaceX IPO Filing", "url": "https://www.reuters.com/business/spacex-ipo-2026/"},
            {"name": "Reuters — Musk ordered Starlink switched off in Ukraine during Crimea offensive (2022)", "url": "https://www.reuters.com/technology/musks-starlink-restricts-ukraine-operations/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: Pentagon vs SpaceX Starlink price hike during Iran war")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: India-Bangladesh Border Pushbacks
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("india-bangladesh-border-pushbacks-foreigners-tribunal-assam")
if slug2 not in existing_slugs and not any("bangladesh" in h and "push" in h for h in existing_headlines_lower) and not any("bangladesh" in h and "border" in h for h in existing_headlines_lower):
    body2 = """On Sunday, Bangladesh's 60th Battalion of Border Guard Bangladesh began driving through border villages in Brahmanbaria district with loudspeakers mounted on trucks. The message, broadcast in Bengali, was a warning: stay alert. India may be pushing people across the border.

"We have started miking in border villages to raise awareness among residents and ask them to stay vigilant against any illegal crossings or push-in attempts," Lieutenant Colonel S. M. Shariful Islam, the battalion commander, told Reuters. "Our patrols and surveillance have been strengthened across the border areas."

This is not a routine border patrol announcement. It is the response of a sovereign nation to what it describes as a systematic operation by its neighbour to force people across a 4,096-kilometre frontier — one of the longest land borders in the world.

## What India Is Doing

Since May 2025, India's northeastern state of Assam has been executing what officials describe as the enforcement phase of the National Register of Citizens process. Foreigners' tribunals — quasi-judicial bodies established under the Foreigners Act of 1946 — have declared approximately 30,000 people to be non-citizens. Of these, hundreds have already been physically escorted to the Bangladesh border and pushed across.

The process works like this: a person is summoned before a foreigners' tribunal, usually on the basis of a complaint or a discrepancy in their documentation. The tribunal reviews their documents — birth certificates, school records, voter rolls, land records — and determines whether they can prove Indian citizenship. If they cannot, they are declared a "foreigner." Once declared, they are subject to detention and deportation.

Human rights organizations including Amnesty International and Human Rights Watch have documented cases in which the process has been applied to people who have lived in India for decades — in some cases, their entire lives. Families have been split. People who speak no Bengali, who have never been to Bangladesh, who hold Indian voter ID cards, have been escorted to the border and told to cross.

The Indian government's position is clear. The BJP, which governs Assam, Tripura, and West Bengal — the three states that share borders with Bangladesh — has declared tackling undocumented migration a national priority. India's foreign ministry told reporters earlier this month that it has asked Bangladesh to verify the nationality of more than 2,860 people suspected of being Bangladeshis living illegally in India.

Bangladesh's position is equally clear: any repatriation must follow formal bilateral procedures. Unilateral push-ins across the border are not repatriation. They are, in Dhaka's view, a violation of international law.

## The Supreme Court Intervenes

The Indian Supreme Court has been drawn into the dispute. In a hearing earlier this year, the court examined the case of Sonali Khatun — a woman who was picked up by Delhi police from her workplace in Rohini, where she had lived for over two decades as a daily wage earner, and pushed across the Bangladesh border along with her eight-year-old child.

Khatun claimed to be an Indian citizen from Birbhum district in West Bengal. The police classified her as a Bangladeshi. She was deported without a tribunal hearing, without a court order, without any formal determination of her nationality. Her eight-year-old child was deported with her.

The Supreme Court ordered the government to bring Khatun and her child back to India on humanitarian grounds. In subsequent hearings, Solicitor General Tushar Mehta told the court that the government had decided to bring back some of the deported individuals and verify their citizenship status. He estimated it could take eight to ten days.

The Calcutta High Court had earlier quashed the Centre's decision to deport Khatun and another woman, Sweety Bibi, also from Birbhum district, calling the deportation arbitrary and illegal. The government appealed to the Supreme Court but, facing scrutiny over the lack of due process, agreed to bring them back.

These cases are not isolated. They represent a pattern in which people are identified as potential foreigners — often on the basis of their names, their appearance, or the neighbourhoods they live in — and removed from the country without the due process that Indian law itself requires.

## The Scale of the Problem

The 30,000 people declared foreigners by Assam's tribunals are a small fraction of the approximately 1.9 million people excluded from the National Register of Citizens when it was published in 2019. The NRC was a massive documentation exercise that required every resident of Assam to prove, with documents, that they or their ancestors were in India before March 24, 1971 — the eve of the Bangladesh Liberation War.

Of the 33 million people who applied, 1.9 million were excluded. Many of them are ethnic Bengalis — both Hindu and Muslim — whose families have lived in Assam for generations but who lack the specific documents the NRC required. Some are illiterate. Some lost documents in floods — Assam is one of the most flood-prone regions in the world. Some never had the documents the NRC demands because the bureaucratic infrastructure that would have produced them did not exist in the rural Assam of the 1960s and 1970s.

The excluded 1.9 million have been filing appeals through the foreigners' tribunals. The tribunals are overwhelmed. The process is glacially slow. And the outcomes have been contested — studies by organizations including the National Law University Delhi have found that tribunal proceedings are frequently marked by procedural irregularities, lack of legal representation, and evidentiary standards that place an impossible burden on the accused.

Meanwhile, the BJP government has been clear about its intent. The Citizenship Amendment Act of 2019, which grants accelerated citizenship to Hindu, Sikh, Buddhist, Jain, Parsi, and Christian refugees from Pakistan, Bangladesh, and Afghanistan — but not Muslims — was designed to work in conjunction with the NRC. Hindus excluded from the NRC could seek citizenship through the CAA. Muslims excluded from the NRC could not.

The combined effect of the NRC and the CAA, critics have argued, is a system that systematically strips citizenship from Muslims while providing a safety net for everyone else. The government has denied this characterization. The Supreme Court has not ruled on the constitutionality of the CAA in the context of the NRC.

## The Human Geography

The India-Bangladesh border is unlike most international frontiers. It cuts through villages. It divides families. It runs through rice paddies, along rivers, through markets where people from both sides have traded for centuries. In many places, there is no fence, no wall, no visible marker — just a line on a map that was drawn by Cyril Radcliffe in 1947, a British lawyer who had never been to India before he was asked to partition it.

The border's porousness has made it both a lifeline and a flashpoint. Families maintain relationships across it. Traders cross it daily. Migrant workers — millions of them — have crossed it over decades, in both directions, driven by floods, famines, political violence, and economic opportunity.

The question of who belongs on which side of this line has been contested since 1947. The NRC was supposed to settle it. Instead, it has reopened every wound.

## What Bangladesh Fears

Bangladesh's concern is not just about the immediate pushbacks. It is about precedent.

If India establishes the practice of unilaterally declaring residents to be foreigners and pushing them across the border, Bangladesh — a country of 170 million people with a per capita income one-third of India's — becomes the default destination for everyone India decides is not Indian. Bangladesh has no mechanism to absorb these people. It has no housing for them. It has no social services. It already hosts approximately 1.1 million Rohingya refugees from Myanmar.

Bangladesh's foreign ministry has repeatedly warned that unilateral push-ins are unacceptable. But Bangladesh's leverage over India is limited. India controls Bangladesh's access to its upstream water resources. India is Bangladesh's largest trading partner. India's intelligence services maintain deep relationships with Bangladesh's security establishment. The power asymmetry is total.

The loudspeakers in Brahmanbaria are Bangladesh's response — public awareness campaigns, increased patrols, intelligence operations. It is the response of a country that cannot stop what India is doing, but wants its own citizens to know it is happening.

## What NRIs Are Watching

For the Indian diaspora, the pushback crisis resonates on two frequencies.

The first is political. The NRC-CAA combination is the most consequential citizenship policy India has undertaken since independence. It determines who is Indian. For NRIs — many of whom hold OCI cards, maintain Indian property, send children to Indian schools, and plan to retire in India — the question of what constitutes Indian citizenship is not abstract. It is the legal foundation of their connection to the country.

The second frequency is personal. Many NRIs have experienced, from the other side, what it means to have your citizenship questioned by a bureaucracy. Indians in the United States have watched ICE agents detain people with valid visas. They have seen the H-1B system weaponized to create uncertainty about who belongs. They have felt the anxiety of documentation — of being asked to prove, with papers, that you are who you say you are and that you have the right to be where you are.

The people being pushed across the Bangladesh border are not NRIs. They are among the poorest people in India. They are daily wage earners, domestic workers, rickshaw pullers. They do not have lawyers. They do not have political connections. They do not have the resources to fight a foreigners' tribunal.

But the principle is the same. Citizenship is either a right that the state must prove you lack, or it is a privilege that you must prove you deserve. The NRC and the pushbacks have answered that question for India: you must prove you deserve it. And the burden of proof falls heaviest on those who have the least ability to meet it."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "India Has Pushed Hundreds of People Across the Bangladesh Border. Foreigners' Tribunals Declared Them Non-Citizens. Some Had Lived in India Their Entire Lives. The Supreme Court Ordered the Government to Bring Them Back.",
        "subheadline": "Bangladesh's border guards have intensified patrols and launched loudspeaker campaigns along the frontier after India pushed hundreds of people — declared foreigners by quasi-judicial tribunals in Assam — across the 4,096-kilometre border. The Supreme Court intervened after a woman and her eight-year-old child were deported from Delhi without a hearing. Of 30,000 people declared foreigners, many have lived in India for decades. The NRC excluded 1.9 million from citizenship. The CAA provides a path back for Hindus, Sikhs, Buddhists — but not for Muslims. Bangladesh says unilateral push-ins violate international law.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "For NRIs, the pushback crisis resonates on two levels. First, the NRC-CAA framework determines who is Indian — a question that matters to every OCI holder, every NRI with Indian property, and every family planning to return. Second, the experience of having citizenship questioned by a bureaucracy is one many NRIs have lived from the other side: ICE detentions, H-1B uncertainty, documentation anxiety. The people being pushed into Bangladesh are among India's poorest — daily wage earners with no lawyers and no political connections. But the principle is the same: citizenship is either a right that the state must prove you lack, or a privilege you must prove you deserve. The NRC has answered that question for India.",
        "tags": ["India", "Bangladesh", "border", "pushback", "NRC", "CAA", "foreigners tribunal", "Assam", "deportation", "Supreme Court", "citizenship", "Sonali Khatun", "Brahmanbaria", "Cyril Radcliffe", "NRI", "OCI", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Bangladesh boosts vigilance over suspected forced crossings from India", "url": "https://www.reuters.com/world/asia-pacific/bangladesh-boosts-vigilance-over-suspected-forced-crossings-india-2026-05-26/"},
            {"name": "LiveLaw — Centre Agrees In Supreme Court To Bring Back Persons Deported To Bangladesh", "url": "https://www.livelaw.in/top-stories/centre-bring-back-persons-deported-bangladesh-supreme-court/"},
            {"name": "DevDiscourse — Decided to bring back to India some persons deported to Bangladesh: Centre to SC", "url": "https://www.devdiscourse.com/article/law-order/centre-bring-back-deported-bangladesh/"},
            {"name": "TBS News — Delhi tells Indian Supreme Court it will bring back persons allegedly 'pushed' to Bangladesh", "url": "https://www.tbsnews.net/bangladesh/delhi-tells-indian-supreme-court-pushback-bangladesh/"},
            {"name": "ORF — Does India Stand To Lose Bangladesh's Friendship Over CAA-NRC", "url": "https://www.orfonline.org/research/does-india-stand-to-lose-bangladeshs-friendship-over-caa-nrc/"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: India-Bangladesh border pushbacks / NRC / Supreme Court")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # Image sourcing — Wikipedia first for person articles, Pexels fallback
    img_url = None
    img_attribution = "The Videshi"

    if i == 0:
        # SpaceX / Pentagon — Elon Musk is the central figure
        img_url = fetch_wikipedia_person_image("Elon Musk")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            img_url = fetch_pexels_image("satellite orbiting earth space", "military drone technology")
    elif i == 1:
        # India-Bangladesh border — no single person, use Pexels with specific terms
        img_url = fetch_pexels_image("India Bangladesh border fence", "border crossing checkpoint South Asia")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": img_attribution
            })
            print(f"  ✓ Image linked (attribution: {img_attribution})")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: Pentagon-SpaceX Starlink price hike + India-Bangladesh border pushbacks ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
