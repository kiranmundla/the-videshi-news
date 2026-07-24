#!/usr/bin/env python3
"""
The Videshi — News Writer (2026-05-27 evening batch)
Publishes 3 articles to Supabase with Wikipedia/Pexels images.
"""

import os, json, requests, urllib.parse, datetime, subprocess

# --- Load Supabase creds ---
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, val = line.split("=", 1)
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

pexels_env = os.path.expanduser("~/workspace/.env.pexels")
PEXELS_KEY = None
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            if "PEXELS_API_KEY" in line:
                PEXELS_KEY = line.split("=", 1)[1].strip().strip('"').strip("'")


def fetch_wikipedia_person_image(person_name):
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
                print(f"  ✓ Wikipedia image for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    if not PEXELS_KEY:
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {PEXELS_KEY}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            for photo in data.get("photos", []):
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if r.status_code == 200 and "image" in ct and cl > 5000:
            print(f"  ✓ Validated: {cl} bytes")
            return True
        print(f"  ⚠ Failed: status={r.status_code}, type={ct}, size={cl}")
    except Exception as e:
        print(f"  ⚠ Validate error: {e}")
    return False


def get_image(person=None, pexels_q=None, pexels_fallback=None):
    """Try Wikipedia for person, then Pexels fallback."""
    img = None
    attr = "Pexels"
    if person:
        img = fetch_wikipedia_person_image(person)
        if img and validate_image(img):
            return img, "Wikimedia Commons"
        img = None
    if pexels_q:
        img = fetch_pexels_image(pexels_q, pexels_fallback)
        if img and validate_image(img):
            return img, "Pexels"
    return "", "None"


def publish(article):
    r = requests.post(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, json=article, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            print(f"  ✓ PUBLISHED: {result[0].get('headline', '')[:70]}...")
            return True
    print(f"  ✗ FAILED: {r.status_code} — {r.text[:300]}")
    return False


now = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

# =========================================================================
# ARTICLE 1: Rubio India Visit
# =========================================================================
print("\n" + "="*60)
print("ARTICLE 1: Rubio India Visit")
print("="*60)

img1, attr1 = get_image(person="Marco Rubio", pexels_q="India US diplomacy flags meeting")

body1 = """Secretary of State Marco Rubio wrapped up a four-day, four-city tour of India this week — his first visit to the country in his dual role as Secretary of State and National Security Advisor — with a $500 billion purchase commitment, a deepening nuclear partnership, and a barely veiled warning about Russian and Iranian crude.

The trip, which included stops in Kolkata, Agra, Jaipur, and New Delhi alongside a Quad meeting, came at a moment of acute vulnerability for India. The country imports nearly 88 percent of its crude oil, more than half of it transiting the Strait of Hormuz. Three months into the Iran war, that supply line has never looked more fragile.

## The $500 Billion Headline

In an X post on Saturday, Rubio announced that Delhi had committed to purchasing $500 billion in American goods over the next five years, focused on energy, technology, and agriculture. "We want to sell them as much energy as they'll buy," Rubio told reporters before departing. "They're a great ally, a great partner."

The commitment signals a strategic rebalancing. India has continued buying discounted Russian crude despite Western sanctions, and Venezuelan oil has surged — Caracas recently overtook Saudi Arabia and the United States to become India's third-largest crude supplier. Washington is now hoping to redirect that purchasing power toward American oil and liquefied natural gas.

"India cannot be a strategic energy partner for Washington while Indian firms are repeatedly surfacing in sanctions designations involving Iranian energy flows, shadow fleet shipping, and falsified origin claims," said Max Meizlish, a research fellow at the Foundation for Defense of Democracies.

## The Nuclear Prize

The real long-term story may be nuclear. India hit a major milestone last month when its Prototype Fast Breeder Reactor at Kalpakkam in Tamil Nadu achieved criticality on April 6 — a self-sustaining nuclear chain reaction for the first time. The 500-megawatt reactor, designed by the Indira Gandhi Centre for Atomic Research, took 22 years to complete.

Unlike conventional reactors, fast breeder reactors produce more fissile material than they consume, potentially freeing India from dependence on imported uranium. Once fully operational, India will become only the second country after Russia to run a commercial fast-breeder reactor.

India plans to scale its nuclear capacity from 8.8 gigawatts to 100 gigawatts by 2047 — a transformation officials estimate could create a nearly $300 billion nuclear energy market. A 20-member U.S. Executive Nuclear Industry Delegation visited India earlier this month to explore private investment in small modular reactors and advanced nuclear technologies.

## The Reliance Refinery in Texas

The energy relationship is now flowing in both directions. President Trump recently announced a historic $300 billion refinery agreement with Reliance Industries that would build a new oil refinery at the Port of Brownsville in Texas — the first new major U.S. refinery in 50 years. For Mukesh Ambani's Reliance, it is a bet on processing American crude for global export. For Trump, it is jobs and energy independence in a single photo-op.

## The Friction Underneath

Rubio's visit was not all handshakes. The Wall Street Journal reported that "America First shadows" trailed the trip. While Rubio framed trade friction as "not about India, it's about the United States," he also made clear that Trump's agenda would not spare close partners.

India's Russian oil purchases remain a point of irritation. And while both sides talked up the Quad and Indo-Pacific security, the H-1B registration drop of 38.5 percent and Trump's new green card order — requiring applicants to leave the country — have unsettled the Indian American community.

## What It Means for the Diaspora

For Indian Americans and NRIs, Rubio's visit signals that the U.S.-India relationship is evolving from diplomatic rhetoric into industrial-scale infrastructure. A Reliance refinery in Texas, American nuclear technology in Tamil Nadu, and $500 billion in trade commitments create real economic corridors — and real jobs — on both sides.

But the relationship is also becoming more transactional. India is expected to choose American energy over Russian and Iranian crude, and Washington is watching the ledger closely. The next five years will reveal whether the $500 billion commitment is a partnership or a purchase order."""

publish({
    "headline": "Rubio Just Left India With a $500 Billion Deal. The Real Win Was Nuclear.",
    "subheadline": "A four-day, four-city tour produced a trade commitment, a fast-breeder reactor milestone, and a $300 billion Reliance refinery in Texas. But Washington wants India to drop Russian crude first.",
    "body": body1.strip(),
    "slug": "rubio-india-visit-500-billion-deal-nuclear-energy-reliance-texas-refinery-20260527",
    "category": "news",
    "vertical": "geopolitics",
    "status": "published",
    "published_at": now,
    "image_url": img1,
    "image_caption": "U.S. Secretary of State Marco Rubio visited four Indian cities over four days, wrapping up with a Quad meeting.",
    "image_attribution": attr1,
    "sources": json.dumps([
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/energy/rubio-visit-india-pushes-deeper-energy-ties-iran-conflict-rattles-global-oil-markets"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/rubio-says-us-will-either-have-good-agreement-with-iran-or-deal-with-it-another-2026-05-26/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/world/asia/america-first-shadows-visit-by-rubio-to-repair-rift-with-india"},
        {"name": "Press Information Bureau", "url": "https://pib.gov.in/"},
        {"name": "IANS", "url": "https://ianslive.in/"}
    ])
})


# =========================================================================
# ARTICLE 2: West Bengal — BJP Wins, Mamata Refuses to Resign
# =========================================================================
print("\n" + "="*60)
print("ARTICLE 2: West Bengal Political Earthquake")
print("="*60)

img2, attr2 = get_image(person="Mamata Banerjee", pexels_q="India parliament political rally", pexels_fallback="Kolkata India city")

body2 = """For fifteen years, Mamata Banerjee ruled West Bengal with the kind of unyielding grip that made her both admired and feared across India. On May 4, the BJP ended that era, winning more than two-thirds of the state assembly's 294 seats — the party's most significant eastern breakthrough in history.

Banerjee refused to accept it.

## The Result and the Refusal

The BJP's landslide was decisive. The party swept constituencies across the state, including TMC bastions that had seemed impregnable. Opposition leaders from CPI(M) to Congress acknowledged that voters had delivered a clear mandate against TMC's record. CPI(M) State General Secretary Mohammed Salim said the results "clearly indicate that the people have mandated against the TMC's limitless corruption, autocratic rule, and misgovernance."

Banerjee saw it differently. In a defiant press conference hours after the results, she described the outcome as a "murder of democracy" and accused the Election Commission of colluding with the BJP. She pointed to the Special Intensive Revision exercise that preceded the election, in which opposition parties allege nearly 9 million voter names were removed from electoral rolls.

"I won the election," Banerjee told reporters, despite her party losing over 100 seats. She refused to visit Raj Bhavan to tender her resignation.

## The Voter Roll Controversy

The SIR controversy became the central dispute. TMC leaders alleged that minority communities and Matua voters were disproportionately affected by the deletions. The Election Commission responded that the removals targeted duplicates, deceased, and ineligible entries.

The BBC reported on the scale: "Millions removed from voter rolls before West Bengal election." The Guardian described "millions stripped of vote before critical state election." Al Jazeera asked whether Muslims were "the target."

Whether the removals were routine cleanup or targeted disenfranchisement remains bitterly contested. What is not contested is the scale: 9 million names is roughly 10 percent of West Bengal's electorate.

## Governor Dissolves the Assembly

When Banerjee refused to resign, Governor RN Ravi invoked his constitutional authority. On May 7, he dissolved the state legislative assembly and dismissed the cabinet, ending TMC's hold on power.

Constitutional experts largely agreed the Governor's action was within legal bounds. Once a government clearly loses its majority, the chief minister's continuation becomes constitutionally untenable — regardless of personal objections.

Suvendu Adhikari, who had defected from TMC to BJP in 2021, was sworn in as the new Chief Minister. Banerjee did not attend the ceremony.

## Post-Election Violence

The transition was not peaceful. Reports of political clashes and violence emerged from several districts. On May 6, assailants on motorbikes fatally shot Chandranath Rath, Suvendu Adhikari's personal assistant, in what was widely seen as a targeted political assassination. Both BJP and TMC accused each other of intimidation and attacks on party workers.

The violence drew echoes of 2021, when West Bengal saw weeks of post-election clashes that drew national condemnation.

## The Supreme Court Challenge

Banerjee has taken her fight to the Supreme Court, alleging voter roll manipulation and EVM tampering. The court issued notice and listed the petitions for further hearing, but has not stayed the new government's formation.

Rahul Gandhi described the BJP's victory as a "theft of the popular mandate." But even sympathetic observers note that the BJP's margin — over two-thirds of seats — is difficult to attribute solely to voter roll manipulation.

## What It Means

West Bengal's fall reshapes Indian politics. The BJP now controls nearly every major state in eastern India. For the diaspora, the outcome is a reminder that Indian democracy remains turbulent, contested, and intensely local — even as the national narrative increasingly belongs to the BJP.

Mamata Banerjee has not indicated whether she plans to retire or continue fighting. If history is any guide, she will fight."""

publish({
    "headline": "Mamata Refused to Resign After Losing West Bengal. The Governor Dissolved the Assembly Anyway.",
    "subheadline": "The BJP won over two-thirds of seats in its most significant eastern breakthrough. Banerjee called it a 'murder of democracy.' The Supreme Court is now hearing her challenge.",
    "body": body2.strip(),
    "slug": "west-bengal-bjp-wins-mamata-refuses-resign-governor-dissolves-assembly-20260527",
    "category": "news",
    "vertical": "politics",
    "status": "published",
    "published_at": now,
    "image_url": img2,
    "image_caption": "Mamata Banerjee refused to accept the BJP's landslide victory in West Bengal's 2026 assembly elections.",
    "image_attribution": attr2,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/india/indian-chief-minister-refuses-resign-after-election-defeat-modis-bjp-2026-05-05/"},
        {"name": "The Guardian", "url": "https://www.theguardian.com/world/2026/may/04/narendra-modis-bjp-wins-election-in-west-bengal-for-the-first-time"},
        {"name": "BBC News", "url": "https://www.bbc.com/news/articles/west-bengal-voter-rolls"},
        {"name": "Livemint", "url": "https://www.livemint.com/politics/"},
        {"name": "Wikipedia", "url": "https://en.wikipedia.org/wiki/2026_West_Bengal_election_controversies"}
    ])
})


# =========================================================================
# ARTICLE 3: Ebola — 'Breakneck' Epidemic
# =========================================================================
print("\n" + "="*60)
print("ARTICLE 3: Ebola Epidemic")
print("="*60)

img3, attr3 = get_image(pexels_q="hospital medical workers protective equipment Africa", pexels_fallback="health workers epidemic response")

body3 = """The Ebola outbreak in the Democratic Republic of Congo has surpassed 2,000 identified contacts — people who may have been exposed to the virus — and health teams have managed to find and follow up with only 7 percent of them.

The numbers, revealed in WHO coordination documents this week, paint a picture of an epidemic that is accelerating faster than the world's ability to contain it.

"The outbreak is outpacing the response," WHO Director-General Tedros Adhanom Ghebreyesus said on Wednesday. "Attacks on health facilities make tracking cases and their contacts nearly impossible."

## The Deadliest Strain Without a Vaccine

This is not the Ebola the world has fought before. The Bundibugyo strain driving the current outbreak has no approved vaccine and no proven treatment. During the 2018-2020 Congo outbreak, vaccines helped contain the Zaire strain. This time, health workers have nothing to offer beyond isolation and supportive care.

As of this week, the outbreak has caused at least 220 suspected deaths and over 900 cases across three provinces in eastern Congo. Seven cases have been confirmed in Uganda, marking cross-border spread. The International Rescue Committee has warned it could become the "deadliest on record," surpassing the 2014-2016 West Africa epidemic that killed over 11,000 people.

## A War Zone Wrapped in an Epidemic

Eastern Congo's Ituri province — the outbreak's epicenter — is one of the most difficult places on earth to mount a health response. The region has been ravaged by armed conflict for years, with millions displaced and health infrastructure in ruins.

Hospitals have been attacked. Isolation tents have been burned by angry mobs reclaiming bodies of loved ones, unaware that infectious corpses remain dangerous. Health workers themselves are dying.

"If you had to choose a bad place for this to happen, it would be Ituri," said Professor Salim Abdool Karim, a South African epidemiologist advising Africa CDC.

The virus circulated undetected for six weeks before the outbreak was officially declared on May 15. By then, the chains of transmission had spread far beyond what contact tracers could follow.

## The U.S. Withdrawal Created a Vacuum

The U.S. exit from the WHO — formalized in January — has created a gap that multiple health sources described as devastating. Previously, the U.S. often co-led international Ebola responses. Now, the organizations that would normally coordinate are either defunded or absent.

"The organisations that would have been able to do this work are not there anymore," one U.S. official briefed on the response told Reuters.

CARE's country director said his emergency response team had been cut by a third. Doctors Without Borders has issued a global call for staff to reinforce its Congo team. The CDC has activated a Level 2 emergency response and imposed entry restrictions for travelers from Congo, Uganda, and South Sudan.

## India's Response

India has moved faster than most. The government launched screening and surveillance at airports and other entry points across the country, including dedicated camps at Chennai and Vijayawada airports. Citizens have been advised to avoid non-essential travel to Congo, Uganda, and South Sudan.

India's airports use self-declaration forms and in-flight alerts for passengers from affected regions, with protocols for immediate medical attention if symptoms appear within 21 days. India also shipped emergency medical supplies to Congo earlier this month.

The Bengaluru scare — when a Ugandan woman was quarantined for suspected Ebola after traveling through Ahmedabad — ended with a negative test result, confirming that India's screening protocols functioned as designed.

## What Comes Next

Without a vaccine, the only tools available are the oldest ones in epidemiology: find contacts, isolate the sick, safely bury the dead. Right now, 93 percent of known contacts remain untraced.

"We're going back to the basics of Ebola outbreak responses when we didn't have the means to contain it like we did before vaccines and therapeutics," said Dr. Alan Gonzalez of Doctors Without Borders.

For the diaspora — especially Indians working in East Africa or with travel to the region planned — the message from global health authorities is unambiguous: this outbreak is not contained, the strain is untreatable, and the response is falling behind. Act accordingly."""

publish({
    "headline": "The Ebola Epidemic Just Hit 2,000 Exposed Contacts. Only 7 Percent Have Been Found.",
    "subheadline": "The Bundibugyo strain has no vaccine. The WHO says the outbreak is 'outpacing the response.' India has tightened airport screening, but the global health system built to contain this is falling apart.",
    "body": body3.strip(),
    "slug": "ebola-congo-2000-contacts-7-percent-traced-breakneck-epidemic-india-screening-20260527",
    "category": "news",
    "vertical": "health",
    "status": "published",
    "published_at": now,
    "image_url": img3,
    "image_caption": "Health workers in protective equipment respond to the Ebola outbreak in eastern Congo.",
    "image_attribution": attr3,
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/breakneck-ebola-epidemic-congo-outpaces-worlds-response-2026-05-27/"},
        {"name": "Reuters — Travel rules", "url": "https://www.reuters.com/world/countries-tighten-travel-rules-ebola-risk-rises-2026-05-27/"},
        {"name": "WHO", "url": "https://www.who.int/"},
        {"name": "People", "url": "https://people.com/ebola-outbreak-deadliest-record-aid-group-warns/"},
        {"name": "Curly Tales", "url": "https://curlytales.com/"}
    ])
})

print("\n" + "="*60)
print("DONE — 3 articles processed")
print("="*60)
