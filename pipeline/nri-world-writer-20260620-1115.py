#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

env_file = Path.home() / ".env.supabase"
if not env_file.exists():
    env_file = Path.home() / "workspace" / ".env.supabase"
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

article1_body = """A renowned Chicago Indian restaurant is heading to the desert, and its arrival says something about how far Indian cooking has travelled in the American imagination.

NADU, the regional Indian restaurant that chef Sujan Sarkar opened in Chicago in the spring of 2025, is opening a second U.S. location this month at Desert Ridge Marketplace in Phoenix. The team behind it already runs Feringhee in nearby Chandler, so the Valley is familiar ground. What is new is the proposition: a restaurant that earned a clutch of national honours in its first year is now betting that a suburban Arizona shopping district is ready for the kind of Indian food that wins awards rather than just feeds homesick students.

## Context & Background

The accolades are not trivial. Within twelve months of opening, NADU was named one of the Best New Restaurants in America by Eater, earned a James Beard Award semifinalist recognition for Best New Restaurant, and picked up a MICHELIN Bib Gourmand designation. For a cuisine that spent decades pigeonholed in America as cheap, brown, buffet-line comfort food, that is a meaningful shift, and it has been a long time coming.

For the diaspora, the significance runs deeper than a good review. Indian restaurants in America have historically been survival businesses, opened by immigrants who cooked because it was the most bankable skill they carried across the ocean. The food was flattened to suit unfamiliar palates: the same nine dishes from Punjab and Bengal, the heat dialled down, the regional specificity sanded off. A generation of Indian-Americans grew up slightly embarrassed by the strip-mall curry house even as they relied on it.

## Current Developments

NADU represents the opposite instinct. Sarkar, who built his reputation in fine dining before opening the Chicago original, has framed the restaurant around the idea that Indian food is far broader than the handful of dishes the world already knows.

"We want NADU to reflect the type of cuisine traditionally enjoyed in my home country of India — simple, bold, and full of flavor," Sarkar said in a news release announcing the Phoenix opening. "Our goal is to highlight the beauty of regional Indian cooking in an approachable way, with flavors people recognize and love."

The Phoenix kitchen will be led by executive chef Pujan Sarkar, Sujan's brother and longtime mentee — a detail that underlines how much of this new wave is still, at heart, a family enterprise. The difference is the ambition. Where the previous generation opened restaurants to make a living, this one is opening them to make a statement.

## Diaspora Impact

It is part of a broader pattern. Across the country, Indian-origin chefs are reframing what their food can be once it puts down roots in American soil. In Arizona, the Scottsdale-area bar Indibar — built by two former Taj Dubai chefs around indigenous Sonoran ingredients like the drought-hardy tepary bean — was recently named one of USA Today's Restaurants of the Year. In Los Angeles, the Badmaash family has built a following with a defiantly un-traditional aesthetic, projecting Bollywood classics on the walls and serving Indian tacos. In the City of London, India-based restaurateurs are opening contemporary diners that serve forest-pepper crab dosa and Kerala small plates to audiences who have never set foot in a tandoori house.

What links them is a refusal to apologise. For diaspora diners, that refusal is the point. A restaurant that treats dal with the same reverence a French kitchen gives a sauce, that names its regional sources, that trains its servers to explain rather than soften — that is a restaurant making an argument about belonging. The food is no longer asking permission to exist in America. It is claiming a place at the centre of the table.

The economics help. Indian-Americans are now among the highest-earning demographic groups in the United States, and a second generation with disposable income and cultural confidence is willing to pay fine-dining prices for the food it grew up with. Where the first generation needed the buffet to be cheap, the second wants it to be excellent — and is prepared to fund the difference.

## What's Next

Whether Desert Ridge shoppers embrace regional Indian fine dining at scale remains an open question; the suburbs are an unforgiving testing ground. But the direction is set. The arc of Indian food in America has bent from necessity toward artistry, and restaurants like NADU are the proof. For a community that once kept its best cooking behind the kitchen door of the family home, watching it earn Michelin recognition in a Phoenix mall is its own small marker of arrival."""

article2_body = """Within two weeks this spring, three Hindu temples in California's Bay Area were hit: one defaced with separatist graffiti, another with anti-India slogans, a third burgled. The pattern was not random, and the community has stopped treating it as such.

On June 9, the Hindu American Foundation (HAF) wrote to the California Civil Rights Department's Commission on the State of Hate, documenting what it described as a surge in bias incidents, vandalism and targeted violence against Hindu Americans. The letter is a small bureaucratic act with a large subtext: a diaspora that has long preferred to keep its head down is now formally demanding that the state count it among the communities at risk.

## Context & Background

The incidents themselves have become grimly familiar. The Swaminarayan temple in Newark was defaced with anti-India graffiti. Two weeks later, Vijay's Sherawali Temple in nearby Hayward sustained what HAF called a "copycat defacement" with pro-Khalistan graffiti — one week after a theft at the Shiv Durga temple in the same area. Three houses of worship, one cluster, a single message.

"Another Bay Area Hindu temple attacked with pro-Khalistan graffiti," HAF wrote on X, sharing photographs of the Hayward defacement and urging temple leaders to install security cameras and alarm systems. The U.S. State Department's bureau for South and Central Asian Affairs condemned the Newark vandalism and welcomed local police efforts to hold those responsible accountable.

The Indian government has taken notice too. External Affairs Minister S. Jaishankar, asked about the incidents, said the Indian consulate had lodged complaints with U.S. authorities. "Extremists and separatist forces outside India should not get space," he said.

## Current Developments

What makes the HAF letter notable is its venue. The Commission on the State of Hate is a relatively new California body charged with mapping the landscape of bias in the state and recommending responses. By submitting formal testimony, Hindu American advocates are insisting that anti-Hindu bias belongs on that map — a category that has often been overlooked in official hate-crime tallies, which tend to track religion in broader strokes.

The push is part of a longer institutional maturation. For decades, the Indian diaspora in America channelled its energy into private success: degrees, jobs, homes, temples built quietly in suburban office parks. Public advocacy felt unnecessary, even unseemly. That calculation is changing as the community grows large enough, and visible enough, to become a target.

## Diaspora Impact

The vandalism lands on a community already feeling exposed. Santa Clara County's District Attorney has issued public-service announcements urging vigilance during the Hindu festival season, citing past crimes — including a 2022 case in which a man was convicted of hate crimes after assaulting at least 14 South Asian women and stealing their jewellery. The festival calendar, once a season of unguarded celebration, now comes with a safety briefing.

The anxiety is not confined to the United States. Research bodies tracking sentiment have documented rising hostility toward Indian immigrants in Australia, Canada and Ireland, where newer waves of Indian students have been cast, variously, as symbols of unchecked migration or competitors for scarce housing. A 2025 Pew survey across 24 countries found views of India sharply divided, with several nations recording majority-unfavourable attitudes — perceptions that researchers say translate into prejudice against the diaspora itself.

For families who built lives abroad on the promise of safety and meritocracy, the defaced temple wall is a discordant note. It raises the question that the widow of Srinivas Kuchibhotla — the Indian engineer shot dead in a Kansas bar in 2017 — asked the country years ago, and that still has no settled answer: "Do we belong?"

## What's Next

HAF's strategy is to convert that unease into institutional response: security grants for houses of worship, explicit tracking of anti-Hindu incidents, and recognition from bodies like California's hate commission. Whether the state acts remains to be seen; commissions move slowly, and the diaspora's place in the official hierarchy of protected communities is still being negotiated.

But the shift in posture is the story. A community that once responded to a defaced wall by quietly repainting it is now writing letters to the state, lodging diplomatic complaints, and installing cameras. The temples are still standing. What has changed is that their congregations have decided to be counted."""

article3_body = """The oldest Indian-American organisation in the United States held a swearing-in ceremony this month, and the guest list read less like a club roster than a census of how far the community has come.

The Association of Indians in America (AIA), founded in 1967 and the country's first national body for Indian immigrants, inaugurated its National Executive Council for 2026–27 in a grand ceremony in the New York area. The proceedings were studded with the kind of recognition that would have been unimaginable to the organisation's founders: congratulatory letters from New York Attorney General Letitia James, a proclamation from Senator Chuck Schumer, and messages from India's Ambassador to the United States, Vinay Kwatra, and the Consul General of India in New York, Binaya S. Pradhan.

## Context & Background

AIA was born in a very different America. When a handful of Indian immigrants founded it in 1967, the community was tiny — the liberalising 1965 Immigration Act had only just begun to reshape who could enter the country, and Indians abroad were a curiosity rather than a constituency. The organisation's early work was elemental: lobbying for Indians to be counted as a distinct category on the U.S. census, building cultural institutions, giving a scattered population a shared address.

Nearly six decades later, the ceremony's cast of dignitaries measures the distance travelled. State and federal officials now court the Indian-American vote and voice. Diplomats from New Delhi treat community organisations as partners. The swearing-in featured a soulful rendition of the American national anthem and a classical Kathak performance by dancer Esha Mishra, followed by the Indian national anthem led by Jyoti Gupta and AIA members — a tidy choreography of dual belonging, each anthem given its due.

## Current Developments

The new council inherits an organisation that has shifted from advocacy of necessity to advocacy of influence. Among those marking the occasion was Padma Shri Sudhir Parikh, the physician-publisher whose presence connects AIA to a wider network of diaspora institutions. The evening's congratulatory roll call — from Nassau County's comptroller to local town supervisors and clerks — illustrated how thoroughly Indian-American organisations have woven themselves into the fabric of suburban American civic life.

It is a pattern repeating across the country. In Connecticut, the Global Organization of People of Indian Origin (GOPIO-CT) recently marked its 20th anniversary with a banquet honouring five Indian-American leaders, drawing a bipartisan group of state lawmakers and India's Deputy Consul General in New York. "The achievements of Indian Americans have become a global benchmark," the diplomat told the gathering, "communities across the world look to replicate the success and impact you have created in the United States."

## Diaspora Impact

The ceremonies can read, to an outsider, as an endless circuit of galas and award nights — and the diaspora's fondness for them is real. But the banquets serve a function beyond self-congratulation. For a community spread thin across a vast country, these gatherings are the connective tissue: the places where second-generation professionals meet the founders who fought for census recognition, where a state senator learns the name of the local Patel who can mobilise a precinct, where the children of immigrants see their heritage performed on a stage flanked by the flags of both their countries.

They also mark a generational handover. Organisations like AIA were built by immigrants who arrived in the 1960s and 1970s and are now ageing out of leadership. The challenge facing every diaspora institution is whether the American-born generation — busier, more assimilated, less reflexively tied to the old country — will take up the work. The swearing-in of a new council is, in part, a wager that it will.

## What's Next

For AIA's incoming leadership, the task is to keep a 59-year-old institution relevant to a community that no longer needs it for survival. The early battles — to be counted, to be seen, to be safe — have largely been won, even as new ones over security and belonging emerge. The question now is what a national Indian-American organisation is for, once its members have arrived.

The answer, judging by the ceremony, is something like stewardship: of memory, of networks, of the hard-won place the community holds in American public life. The founders built the house. The new council's job is to make sure the next generation still wants to live in it."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "An Award-Winning Indian Kitchen Is Opening in a Phoenix Mall. That's a Bigger Deal Than It Sounds.",
        "subheadline": "NADU, a James Beard semifinalist and Michelin Bib Gourmand winner from Chicago, debuts at Desert Ridge — the latest sign that Indian food in America has stopped apologizing.",
        "slug": make_slug("nadu-indian-restaurant-phoenix-debut-michelin-james-beard-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For a generation of Indian-Americans who grew up faintly embarrassed by the strip-mall curry house, the rise of regional Indian fine dining is a marker of cultural arrival — food that no longer asks permission to exist in America.",
        "tags": ["nri", "diaspora", "food", "indian-american", "restaurants", "arizona"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Arizona Republic (azcentral)", "url": "https://www.azcentral.com/story/entertainment/dining/2026/06/17/nadu-indian-restaurant-phoenix-desert-ridge/"},
            {"name": "Restaurant Business", "url": "https://www.restaurantbusinessonline.com/food/year-redefining-indian-food-america"},
            {"name": "The Videshi", "url": "https://thevideshi.com"}
        ]),
        "score_total": 70,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/31860138/pexels-photo-31860138.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Tandoori chicken plated with herb rice in a modern fine-dining presentation, reflecting a new wave of regional Indian cooking in America.",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "After Three Temples Were Hit in Two Weeks, Hindu Americans Are Done Quietly Repainting the Walls",
        "subheadline": "The Hindu American Foundation has formally asked California's hate commission to count anti-Hindu bias — a sign of a diaspora that has decided to be counted.",
        "slug": make_slug("hindu-american-foundation-california-state-of-hate-temple-vandalism-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A community that long preferred private success to public advocacy is now writing letters to the state, lodging diplomatic complaints, and installing security cameras — formally demanding recognition among the communities at risk.",
        "tags": ["nri", "diaspora", "hindu-american", "community-safety", "california", "hate-crime"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com"},
            {"name": "India Abroad (HAF letter to California Commission on the State of Hate)", "url": "https://www.youtube.com/"},
            {"name": "Santa Clara County District Attorney", "url": "https://da.santaclaracounty.gov"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/30253478/pexels-photo-30253478.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "The BAPS Shri Swaminarayan Mandir in Robbinsville, New Jersey, at sunset — one of the landmark Hindu temples built by the American diaspora.",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Oldest Indian Association Swore In a New Board. The Guest List Was a Map of How Far the Community Has Come.",
        "subheadline": "Founded in 1967 to get Indians counted on the U.S. census, the AIA now draws letters from senators and ambassadors — and faces a generational handover.",
        "slug": make_slug("aia-association-indians-america-nec-2026-swearing-in-diaspora-new-york"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The endless circuit of diaspora galas serves a real function: it is the connective tissue binding the founders who fought for census recognition to a second generation that no longer needs the organization for survival.",
        "tags": ["nri", "diaspora", "indian-american", "community-organization", "new-york", "aia"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com"},
            {"name": "The Indian Eye (GOPIO-CT 20th anniversary)", "url": "https://theindianeye.com"}
        ]),
        "score_total": 66,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7005756/pexels-photo-7005756.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A community honoree holds an award before an applauding audience, a scene familiar at Indian-American organizational galas.",
        "image_attribution": "Pexels",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']} ({wc} words): {e}")
