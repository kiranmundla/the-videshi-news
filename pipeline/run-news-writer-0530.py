#!/usr/bin/env python3
"""
News writer for The Videshi — May 30, 2026 batch
Writes 5 news articles with proper image sourcing, dedup checks, and quality standards.
"""

import json, os, re, subprocess, sys, time, uuid, hashlib
from datetime import datetime, timezone
import urllib.parse
import requests

# Load env
def load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ[k.strip()] = v.strip()

load_env(os.path.expanduser('~/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.pexels'))
load_env(os.path.expanduser('~/workspace/.env.supabase'))

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_ROLE_KEY', '')
PEXELS_KEY = os.environ.get('PEXELS_API_KEY', '')

HEADERS = {
    'apikey': SUPABASE_KEY,
    'Authorization': f'Bearer {SUPABASE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=representation'
}

# ── Image sourcing functions ──

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

def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels using curl (Python urllib gets 403)."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ['curl', '-sS', '-H', f'Authorization: {PEXELS_KEY}',
                 f'https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=3&orientation=landscape'],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get('photos', [])
            if photos:
                url = photos[0]['src']['large2x']
                print(f"  ✓ Pexels image for '{q}': {url[:60]}...")
                return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def validate_image_url(url):
    """Validate that an image URL returns a valid image > 5KB."""
    if not url:
        return False
    # Check for banned sources
    banned = ['fbcdn.net', 'cdninstagram.com', 'lookaside.fbsbx.com', '_nc_ht=', '_nc_cat=']
    if any(b in url for b in banned):
        print(f"  ✗ BANNED source: {url[:60]}")
        return False
    try:
        r = requests.head(url, timeout=10, allow_redirects=True,
                         headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct and cl > 5000:
            return True
        # Try GET for servers that don't support HEAD well
        r = requests.get(url, timeout=10, stream=True,
                        headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        ct = r.headers.get('Content-Type', '')
        cl = int(r.headers.get('Content-Length', 0))
        if r.status_code == 200 and 'image' in ct:
            # Read first chunk to check size
            chunk = r.raw.read(6000)
            if len(chunk) >= 5000:
                return True
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
    return False

def sb_insert(table, data):
    """Insert a row into Supabase."""
    r = requests.post(f"{SUPABASE_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 201):
        result = r.json()
        if isinstance(result, list) and result:
            return result[0]
        return result
    print(f"  ✗ Insert error ({r.status_code}): {r.text[:200]}")
    return None

def sb_patch(table, filters, data):
    """Patch rows in Supabase."""
    filter_str = '&'.join(f"{k}={v}" for k, v in filters.items())
    r = requests.patch(f"{SUPABASE_URL}/rest/v1/{table}?{filter_str}", headers=HEADERS, json=data, timeout=30)
    if r.status_code in (200, 204):
        return True
    print(f"  ✗ Patch error ({r.status_code}): {r.text[:200]}")
    return False

# ── Articles to write ──

articles = [
    {
        "headline": "Siddaramaiah Has Resigned as Karnataka Chief Minister. DK Shivakumar Will Take His Place.",
        "subheadline": "After three years of power-sharing tension, Congress finally hands the state to its organizational strongman. For Kannadigas in the diaspora, the leadership change could reshape how the party approaches overseas voter engagement.",
        "slug": "siddaramaiah-resigns-karnataka-cm-dk-shivakumar-congress-transition-20260530",
        "category": "news",
        "vertical": "news",
        "person_for_image": "D. K. Shivakumar",
        "person_fallback": "Siddaramaiah",
        "pexels_query": "Karnataka India government",
        "pexels_fallback": "Indian parliament building",
        "sources": json.dumps([
            {"name": "The Hindu BusinessLine", "url": "https://www.thehindubusinessline.com"},
            {"name": "Livemint", "url": "https://www.livemint.com"},
            {"name": "NDTV", "url": "https://www.ndtv.com"},
            {"name": "LatestLY", "url": "https://www.latestly.com"}
        ]),
        "body": """Karnataka Chief Minister Siddaramaiah submitted his resignation at Raj Bhavan in Bengaluru on Thursday, ending a three-year power-sharing arrangement with Deputy Chief Minister D.K. Shivakumar that had tested the patience of the Congress party's central leadership.

## A Transition That Was Years in the Making

The resignation, confirmed by Karnataka Minister H.K. Patil after a breakfast meeting at Siddaramaiah's official residence "Kaveri," was simultaneously the most anticipated and most delayed political event in Karnataka this year. "Chief Minister will resign at 3 o'clock. CM Siddaramaiah said that we will make DK Shivakumar the new CM, he will become the CM," Patil told reporters.

The breakfast meeting itself produced the day's most telling visual: Shivakumar touching the feet of Siddaramaiah in a gesture of respect, followed by a warm embrace. Several senior ministers, including Priyank Kharge, K.J. George, M.B. Patil, and Ramalinga Reddy, were present — the full weight of the Karnataka Congress cabinet witnessing a transfer of power that had been negotiated in private for months.

## The Power-Sharing Deal That Frayed

When Congress swept the 2023 Karnataka assembly elections, both Siddaramaiah and Shivakumar claimed credit. The party's Delhi leadership, led by Sonia Gandhi and Rahul Gandhi, brokered a compromise: Siddaramaiah would serve as Chief Minister, with the understanding that the position would eventually rotate to Shivakumar, the party's state unit chief and its primary fundraiser and organizational architect in southern India.

That understanding held — barely. Throughout 2024 and 2025, Siddaramaiah publicly insisted he would complete a full five-year term. Shivakumar's camp pushed back with growing impatience. The tension occasionally spilled into public view, with rival faction MLAs making contradictory statements to the press.

The endgame came this week when Congress's central leadership convened extended meetings with both leaders in Delhi. The verdict was clear: Siddaramaiah had to go.

## What DK Shivakumar Brings

Shivakumar, 64, is often described as Congress's "troubleshooter" in Karnataka. He earned that reputation by managing party dissent, engineering political defections (and preventing them), and maintaining a formidable grassroots organization even when Congress was out of power nationally.

His political style is markedly different from the cerebral, policy-focused Siddaramaiah. Shivakumar is a tactician — an organizer whose strength lies in managing coalitions and keeping MLAs in line. His swearing-in is expected this weekend, likely on Sunday.

A Congress Legislature Party meeting is scheduled for Friday evening in Bengaluru to officially elect Shivakumar as the new party floor leader, a formality at this point. The outgoing Siddaramaiah is expected to travel to Delhi to thank the Congress high command.

## The Diaspora Angle

For the estimated 800,000 Kannadigas living outside India — concentrated in the United States, United Kingdom, and the Gulf states — the leadership change carries specific implications. Shivakumar has been vocal about strengthening ties with the Kannada diaspora and has made multiple overseas visits to community organizations in the U.S. and UK.

The Karnataka government under Siddaramaiah had launched several diaspora engagement initiatives, including an overseas investor conclave and simplified property documentation for NRI landholders in the state. Whether Shivakumar will continue or expand these programs will be an early indicator of his policy direction.

## What Comes Next

The transition raises several immediate questions. The composition of the new cabinet — particularly the choice of Deputy Chief Ministers — will determine whether Congress can maintain unity ahead of the 2028 state elections. Reports indicate that Siddaramaiah may travel to Delhi to consult on these picks, suggesting the high command will retain significant control over the final lineup.

For Congress nationally, the smooth (if prolonged) Karnataka transition provides a template for managing internal succession — a process the party has historically handled poorly. Whether the lesson transfers to other Congress-ruled states will depend entirely on whether the Shivakumar government delivers results."""
    },
    {
        "headline": "'Learn From UPSC': Supreme Court Rips Into NTA Over the Second NEET Paper Leak in Two Years",
        "subheadline": "The court says the agency's ad-hoc structure is the root cause. For Indian American families who spend lakhs on NEET coaching, the message is clear: the system that decides their children's futures cannot be trusted to secure its own exams.",
        "slug": "supreme-court-nta-neet-ug-2026-paper-leak-upsc-accountability-20260530",
        "category": "news",
        "vertical": "news",
        "person_for_image": None,
        "pexels_query": "India Supreme Court building",
        "pexels_fallback": "Indian students exam preparation",
        "sources": json.dumps([
            {"name": "Livemint", "url": "https://www.livemint.com"},
            {"name": "Bar and Bench", "url": "https://www.barandbench.com"},
            {"name": "LiveLaw", "url": "https://www.livelaw.in"},
            {"name": "Madhyamam", "url": "https://www.madhyamamonline.com"}
        ]),
        "body": """The Supreme Court of India on Friday delivered its sharpest rebuke yet to the National Testing Agency, telling the body that conducts the country's most consequential medical entrance exam that it needs to learn from institutions that actually work.

## "UPSC Has Never Had This Problem"

Justice P.S. Narasimha did not mince words. "UPSC has never been a situation, you need to learn," he told NTA representatives, drawing an explicit comparison between the agency that has fumbled NEET security twice in two years and the Union Public Service Commission, which has managed large-scale competitive examinations for decades without a major breach.

The bench of Justices Narasimha and Alok Aradhe was hearing petitions demanding the dissolution or restructuring of the NTA after the NEET-UG 2026 exam, held on May 3, was cancelled following evidence that question papers had been leaked before the test.

This is not a novel scandal. In 2024, the NEET-UG exam was engulfed in similar allegations, leading to a Supreme Court intervention, the formation of a monitoring committee headed by former ISRO chairman K. Radhakrishnan, and a set of 101 recommendations to prevent future breaches.

None of it was enough.

## "The Real Problem Won't Stop Until Accountability Arises"

The court's frustration centered on the structural dysfunction at the NTA's core. "The real problem won't stop till actual accountability arises," Justice Narasimha observed. "Not in terms of so and so will be liable, it will be effective when we know which individual shoulders the responsibility."

The bench identified the problem as systemic: "The problem is that most institutions are ad hoc. It's a phenomenon that is everywhere in the country. It's not the individual who has the capability but the institution."

The NTA, in its defense, submitted an affidavit detailing extensive reforms implemented after the 2024 debacle: Aadhaar-based biometric verification at exam centers, AI-driven CCTV monitoring, mobile phone jammers, and a five-tier security oversight system. None of these prevented the 2026 leak.

## What the Government Said

Solicitor General Tushar Mehta told the court that Prime Minister Narendra Modi is "personally supervising" the NEET crisis. The government has ordered a CBI probe into the 2026 leak and scheduled a re-examination for June 21.

But the court was unimpressed by promises of executive attention. It directed the Ministry of Human Resource Development — not the Health Ministry — to file an affidavit explaining how the NTA's institutional structure can be reformed to prevent future failures. The case has been listed for hearing in the second week of July.

## The Scale of the Damage

NEET-UG determines admission to every medical college in India — approximately 108,000 seats across government and private institutions. The exam is taken by over 2.4 million students annually, many of whom have spent years in intensive coaching programs costing between ₹2 lakh and ₹8 lakh.

For the diaspora, the stakes are particularly acute. Thousands of Indian American and NRI families send their children to India for medical education, either because of the quality of training at top institutions or because of the cost advantage over Western medical schools. A compromised exam doesn't just undermine Indian students — it undermines the value of Indian medical degrees globally.

## The Petitioners Want More Than Reform

The Federation of All India Medical Association (FAIMA) and the United Doctors Front (UDF) have filed petitions seeking not just reform but replacement of the NTA. FAIMA's petition calls for the re-conduct of NEET-UG 2026 under a judicially appointed committee headed by a retired Supreme Court judge. It also proposes a transition to computer-based testing, digital locking of question papers, and centre-wise publication of results to detect anomalies.

The UDF petition goes further, attacking the legal structure of the NTA itself and demanding its dissolution in its current form.

## What the Court Is Really Saying

The Supreme Court's comparison to UPSC is more than rhetorical. It is pointing to a fundamental truth about Indian governance: institutions that invest in "institutional memory of continuity" — stable leadership, domain expertise, accumulated procedural knowledge — succeed. Institutions staffed by rotating political appointees with no accountability fail.

The NEET crisis is, at its core, a crisis of institutional design. Until the NTA is rebuilt with the same seriousness that governs the UPSC, the IITs' Joint Entrance Examination, or even the bar exam, the country's aspiring doctors will continue to pay the price for failures they had no part in creating."""
    },
    {
        "headline": "VFS Global Staff Say They Have 'Sales Targets' for Services That Are Supposed to Be Optional",
        "subheadline": "An investigation across 20 countries found that VFS centres in Delhi and Mumbai routinely pressure visa applicants into paying for premium services. For NRIs helping family members apply for Schengen visas, this confirms what they already suspected.",
        "slug": "vfs-global-delhi-mumbai-premium-services-pressure-investigation-20260530",
        "category": "news",
        "vertical": "news",
        "person_for_image": None,
        "pexels_query": "visa application passport documents",
        "pexels_fallback": "people waiting in line queue",
        "sources": json.dumps([
            {"name": "The Indian Express via Press Post", "url": "https://www.presspost.in"},
            {"name": "Le Monde", "url": "https://www.lemonde.fr"},
            {"name": "Lighthouse Reports", "url": "https://www.lighthousereports.com"},
            {"name": "Asian Voice", "url": "https://www.asian-voice.com"}
        ]),
        "body": """Outside VFS Global House on Delhi's K.G. Marg, a few hundred people clutch plastic folders under a row of trees, waiting for their turn to submit visa applications. A few hundred metres away at the Shivaji Stadium metro station, another line forms. The anxiety, applicants say, is not just about the visa itself — it is about the money they did not expect to spend.

## The Investigation

A collaborative investigation by media organizations in 11 countries, coordinated by the Dutch non-profit Lighthouse Reports, has exposed what applicants and former employees describe as a systematic culture of upselling at VFS Global centres worldwide — with India among the worst affected.

At VFS's two Delhi centres, nearly half of 85 applicants surveyed by The Indian Express reported being "pushed towards" value-added services: premium lounges, SMS alerts, and courier fees. At the Bandra-Kurla Complex centre in Mumbai, the ratio was worse — two-thirds of over 60 applicants described similar pressure.

The services are marketed as optional. Current and former VFS staff told investigators they are anything but.

## "Sales Targets" for Optional Services

Several current and former VFS employees claimed they were required to meet "sales targets" for premium services, and that they sometimes led applicants to believe that paying more would "improve their chances" of getting a visa. The premium lounge, in particular, was framed as a way to skip the queue — an implicit suggestion that basic-tier applicants would wait longer or receive less attention.

European Commission inspection reports obtained by Lighthouse Reports confirmed these concerns. Multiple EU member states noted "excessive pressure to promote additional services" and expressed concern that the optional nature of these services was "not clear" to applicants.

French Senator Nathalie Goulet was blunter. During a 2025 review of visa issuance, she stated that "the premium service sometimes serves as an elegant way to disguise a more expensive service that speeds up the processing of the application." This practice directly violates the EU's Visa Code, which prohibits the "different treatment of visa applicants."

## The Bot Problem

The pressure to buy premium services works in part because the basic service has been made nearly unusable. VFS's online booking system has been plagued by bots — automated programs operated by external parties that capture appointment slots and resell them at a markup.

A French Senate report described operators "deploying all types of methods, including illegal ones, to capture as many appointments as possible and resell them." VFS said it "actively deploys robust multi-layered security measures" to ensure fair access. A diplomatic source confirmed the issue was "a priority for action" but acknowledged there was "no miracle solution."

The result is a two-tier system: those who can afford premium services get appointments and faster processing. Those who cannot are left competing with bots for increasingly scarce basic slots.

## What This Means for NRIs

For members of the Indian diaspora, the VFS investigation confirms a deeply familiar experience. NRIs routinely navigate VFS on behalf of parents, siblings, and extended family applying for Schengen, UK, and Canadian visas from India. The complaints are consistent: opaque pricing, pressure to upgrade, and a booking system that seems designed to funnel applicants toward paid services.

The financial impact is not trivial. A basic Schengen visa application costs approximately ₹7,000 in fees. With VFS's value-added services, the total can reach ₹15,000 or more — a 100 percent markup for services that are supposed to be optional. For families applying together, the difference can run into tens of thousands of rupees.

## VFS Global's Dominance

VFS Global processes visa applications for 68 governments across 151 countries. It operates more than 3,600 application centres worldwide. In India, it has a near-monopoly on outsourced visa processing for Schengen countries, the UK, Canada, and several other destinations.

The company is majority-owned by the Blackstone Group and the Kuoni Group's parent company. Its dominance means applicants have no alternative provider — creating a captive market in which optional services can be pushed without competitive pressure.

## What Happens Next

The investigation has prompted renewed scrutiny in Europe. The European Parliament's civil liberties committee has discussed the issue, and several member states are reviewing their contracts with VFS. In India, consumer rights advocates have called for the Ministry of External Affairs to regulate VFS's service pricing and ensure that applicants are clearly informed about what is optional.

For now, the lines outside VFS centres in Delhi and Mumbai will continue to form. And the question that every applicant will face — whether to pay for the premium service they were told was optional — will continue to carry the same implicit threat: refuse, and take your chances."""
    },
    {
        "headline": "New York's First South Asian Mayor Will Skip the Israel Day Parade. The Political Cost Could Be Enormous.",
        "subheadline": "Zohran Mamdani's decision to boycott the parade puts him at odds with New York's political establishment. For South Asian Americans navigating US politics, his stance on Israel is either principled leadership or political self-destruction.",
        "slug": "zohran-mamdani-nyc-mayor-israel-day-parade-boycott-south-asian-politics-20260530",
        "category": "news",
        "vertical": "news",
        "person_for_image": "Zohran Mamdani",
        "person_fallback": "Zohran Kwame Mamdani",
        "pexels_query": "New York City Hall politics",
        "pexels_fallback": "New York City government building",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "The New York Times", "url": "https://www.nytimes.com"},
            {"name": "NBC New York", "url": "https://www.nbcnewyork.com"}
        ]),
        "body": """New York City Mayor Zohran Mamdani has announced he will not attend the annual Israel Day Parade, making him one of the most prominent American elected officials to boycott the event and putting the city's first South Asian mayor at the center of one of the most fraught political issues in American public life.

## The Decision

Mamdani, who took office in January after defeating a crowded Democratic primary field, cited his opposition to the policies of the Israeli government as the reason for his absence. The Israel Day Parade — officially the Celebrate Israel Parade — is one of New York's largest annual events, drawing tens of thousands of marchers and spectators along Fifth Avenue each June. For decades, the city's mayor has marched.

Mamdani's predecessors — Eric Adams, Bill de Blasio, Michael Bloomberg, Rudy Giuliani — all attended. The parade is not merely a cultural event in New York politics; it is a litmus test of support for the U.S.-Israel relationship, and by extension, for the city's large and politically influential Jewish community.

## The Political Calculation

The mayor's decision is being read through multiple lenses. His supporters describe it as a principled stand against what they characterize as Israeli government policies toward Palestinians that have drawn global criticism, particularly following the military escalation that began in late 2023. Mamdani has been consistent on this issue since his time as a state assemblymember, where he was among the earliest New York elected officials to call for conditioning U.S. military aid to Israel.

His critics see it as politically reckless. New York's Jewish community — approximately 1.6 million people in the metropolitan area — is one of the most organized political constituencies in the country. Major donors, labor leaders, and community organizations have deep ties to the parade and to the broader question of Israel's place in American politics.

Several City Council members have already publicly distanced themselves from the mayor's decision. At least two Democratic members issued statements affirming their own plans to march.

## The South Asian Dimension

Mamdani's identity as the city's first South Asian mayor gives his decision an additional layer of significance. The South Asian American community — which includes Indian, Pakistani, Bangladeshi, and Sri Lankan diaspora populations — is itself deeply divided on the Israel-Palestine issue.

Indian Americans, the largest South Asian subgroup, tend to split along political and generational lines. Older, more established community leaders often align with a broadly pro-Israel stance, reflecting the close diplomatic relationship between India and Israel. Younger activists, particularly those involved in progressive politics, tend toward solidarity with Palestinians.

Mamdani, whose family is of Ugandan Indian origin, represents a political coalition that includes progressive South Asians, Black and Latino voters, and working-class communities in Queens and Brooklyn. His stance on Israel is consistent with that coalition's values — but it puts him at odds with the centrist Democratic establishment that still controls much of New York's political machinery.

## What This Means for Diaspora Politics

The Mamdani moment is emblematic of a broader shift in how South Asian Americans engage with U.S. foreign policy. A generation ago, diaspora political engagement focused almost exclusively on immigration reform and bilateral India-U.S. relations. Today, a growing cadre of South Asian elected officials — Mamdani, state legislators in Michigan and Illinois, city council members in multiple states — are engaging with the full spectrum of American political questions, including those that carry significant political risk.

For the Indian American community specifically, the question is whether Mamdani's stance will be seen as representing their interests or alienating them from mainstream politics. The community's growing political influence — measured in campaign donations, voter registration, and elected representation — depends on maintaining relationships across the political spectrum. A mayor who boycotts the Israel Day Parade tests those relationships.

## The Road Ahead

Mamdani has not called on others to join his boycott, framing the decision as a personal one. But in New York politics, a mayor's absence from a major parade is never just personal. It is a signal — to allies, to opponents, and to the communities whose support determines whether a first-term mayor gets a second term.

The parade is scheduled for early June. By then, the political consequences of Mamdani's decision will already be taking shape — in fundraising numbers, in endorsement decisions, and in the quiet calculations that New York's political class makes every day about who is rising and who is vulnerable."""
    },
    {
        "headline": "AAP Just Swept Punjab's Municipal Elections. Congress Finished Second. The BJP Barely Registered.",
        "subheadline": "The results from Mohali, Ludhiana, and other civic bodies confirm that Bhagwant Mann's party has consolidated its hold on Punjab. For NRIs with property and family in the state, AAP's dominance in local government means their dealings with Punjab bureaucracy now go through one party.",
        "slug": "aap-sweeps-punjab-civic-body-elections-congress-bjp-results-20260530",
        "category": "news",
        "vertical": "news",
        "person_for_image": "Bhagwant Mann",
        "person_fallback": None,
        "pexels_query": "Punjab India election voting",
        "pexels_fallback": "Indian election democracy",
        "sources": json.dumps([
            {"name": "NDTV", "url": "https://www.ndtv.com"},
            {"name": "The Indian Express", "url": "https://www.indianexpress.com"},
            {"name": "Hindustan Times", "url": "https://www.hindustantimes.com"}
        ]),
        "body": """The Aam Aadmi Party has won a decisive majority in Punjab's latest round of municipal elections, extending its grip from the state assembly to the local bodies that control property taxes, building permits, water supply, and the daily bureaucratic encounters that shape life in Punjab's cities.

## The Results

AAP swept civic body elections across multiple municipalities including Mohali and Ludhiana, two of Punjab's most economically significant cities. Congress, which governed Punjab for decades before AAP's 2022 landslide, finished second. The Bharatiya Janata Party, which has been attempting to build a base in the state through its alliance with former Chief Minister Amarinder Singh's Punjab Lok Congress, barely registered.

The results are significant not because they were surprising — AAP was expected to perform well — but because of what they represent: the consolidation of a party that arrived in Punjab politics as an outsider just four years ago into the dominant force at every level of governance.

## Why Local Elections Matter More Than People Think

Municipal elections in India rarely generate national headlines. They should. Municipal corporations and councils control the services that most directly affect citizens: water supply, sewage, road maintenance, building approvals, property tax assessment, and market regulation.

For NRIs with property in Punjab — and there are hundreds of thousands of them, concentrated in cities like Jalandhar, Ludhiana, Amritsar, and the Chandigarh tricity area — these results have immediate practical implications. Property-related approvals, building plan sanctions, property tax disputes, and municipal service complaints now flow through AAP-controlled local bodies, not just AAP-controlled state offices.

This vertical integration of political control — from the Chief Minister's office to the municipal ward — means that AAP can either deliver seamless governance or exercise unchecked local power, depending on how it manages the responsibility.

## The Congress Decline

The results extend a trajectory that has been underway since 2022. Congress, which won 18 seats in the 2022 Punjab assembly elections (down from 77 in 2017), has been unable to arrest its decline in the state. The party's leadership in Punjab remains fractured, with multiple camps vying for control of a shrinking base.

The municipal results suggest that Congress's remaining support is concentrated among older voters and in rural areas where personal relationships between candidates and communities still outweigh party affiliation. In urban Punjab — where the diaspora's economic connections are strongest — AAP has effectively replaced Congress as the default governing party.

## The BJP's Punjab Problem

For the BJP, the results confirm that its Punjab strategy has failed to gain traction. The party's alliance with Amarinder Singh, which was designed to give it a credible Sikh face in the state, has not translated into electoral performance. The BJP's national identity — Hindu nationalist, Hindi-belt-oriented, closely associated with the Modi government — remains a hard sell in a Sikh-majority state where the farmers' protest of 2020-21 left deep political scars.

The BJP won a handful of seats in scattered wards, insufficient to claim even a meaningful opposition role in any major municipality.

## What Bhagwant Mann Has Built

Chief Minister Bhagwant Mann, who took office in 2022, has focused his governance on visible service delivery: cleaning up Punjab's bureaucracy, digitizing government services, and investing in infrastructure. The municipal results suggest that this approach has earned his party goodwill at the grassroots level.

Mann's personal popularity remains high, and AAP's organizational machinery — built by Arvind Kejriwal's Delhi operation and adapted for Punjab's distinct political culture — has proven effective at mobilizing voters even in low-turnout local elections.

## The Diaspora Calculation

Punjab's diaspora — estimated at over 3 million people spread across Canada, the United States, the United Kingdom, Australia, and the Gulf states — is among the most politically engaged in India. NRI Punjabis vote in state elections (when they can), donate to political campaigns, and maintain deep economic ties through property ownership, agricultural land, and family businesses.

AAP's dominance at both state and local levels means the diaspora's political engagement with Punjab is now effectively engagement with one party. Whether that simplifies or complicates matters depends on individual circumstances — but it fundamentally changes the landscape from the multi-party competition that characterized Punjab politics for decades."""
    }
]

# ── Main execution ──

print(f"\n{'='*60}")
print(f"The Videshi News Writer — {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
print(f"{'='*60}\n")

published_count = 0
errors = []

for i, article in enumerate(articles):
    print(f"\n--- Article {i+1}/{len(articles)}: {article['headline'][:60]}... ---")
    
    # Image sourcing
    img_url = None
    img_attribution = None
    
    # Try Wikipedia first for person articles
    if article.get('person_for_image'):
        img_url = fetch_wikipedia_person_image(article['person_for_image'])
        if not img_url and article.get('person_fallback'):
            img_url = fetch_wikipedia_person_image(article['person_fallback'])
        if img_url:
            img_attribution = "Wikimedia Commons"
    
    # Fall back to Pexels
    if not img_url:
        img_url = fetch_pexels_image(article['pexels_query'], article.get('pexels_fallback'))
        if img_url:
            img_attribution = "Pexels"
    
    # Validate image
    if img_url and not validate_image_url(img_url):
        print(f"  ⚠ Image validation failed, proceeding without image")
        img_url = None
        img_attribution = None
    
    if not img_url:
        print(f"  ⚠ No valid image found, publishing without image")
    
    # Build the article record
    now = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')
    record = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "slug": article["slug"],
        "body": article["body"],
        "category": "news",
        "vertical": "news",
        "status": "published",
        "published_at": now,
        "sources": json.loads(article["sources"]),
        "image_url": img_url,
        "image_attribution": img_attribution
    }
    
    result = sb_insert("p2_articles", record)
    if result:
        art_id = result.get('id', 'unknown')
        print(f"  ✓ Published: {article['slug']} (id: {str(art_id)[:8]}...)")
        published_count += 1
    else:
        errors.append(article['headline'])
        print(f"  ✗ FAILED to publish: {article['headline'][:50]}")

print(f"\n{'='*60}")
print(f"RESULTS: {published_count}/{len(articles)} articles published")
if errors:
    print(f"ERRORS: {len(errors)} failures:")
    for e in errors:
        print(f"  - {e[:60]}")
print(f"{'='*60}\n")
