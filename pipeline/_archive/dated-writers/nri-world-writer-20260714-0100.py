#!/usr/bin/env python3
"""NRI World writer — 2026-07-14 01:00 PDT run."""
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
        "headline": "Eleven Thousand Years of India, One Museum in Washington: The Diaspora's Audacious Bid to Tell Its Own Story",
        "subheadline": "An Atlanta-based educationist has spent eight years building a case for a $14 million heritage centre in the American capital. He has now asked the Indian Embassy for a building it bought thirteen years ago.",
        "slug": make_slug("india-heritage-museum-washington-dc-amitabh-sharma-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "A first-of-its-kind museum aimed at helping younger Indian Americans connect with their civilisational heritage, built by and for the diaspora",
        "tags": ["nri", "diaspora", "museum", "heritage", "washington-dc", "indian-american", "culture"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Hindu Business Line", "url": "https://www.thehindubusinessline.com/news/world/indian-diaspora-group-in-us-wants-a-museum-in-washington-dc-to-showcase-vedic-foundation-spiritual-prowess/article71213550.ece"},
            {"name": "India West", "url": "https://www.indiawest.com/news/global_indian/india-heritage-museum-planned-in-washington-d-c/article_64f1b482-3e9b-11ef-a5e2-4f6e5f42d1a0.html"},
            {"name": "IANS via India Post", "url": "https://www.indiapost.com/indian-diaspora-pushes-for-landmark-museum-in-washington/"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/27/Embassy_of_India%2C_Washington%2C_D.C._%2853822530656%29.jpg/3840px-Embassy_of_India%2C_Washington%2C_D.C._%2853822530656%29.jpg",
        "image_caption": "The Embassy of India in Washington, D.C., where organisers have proposed housing the heritage museum",
        "image_attribution": "Wikimedia Commons",
        "body": """Every major diaspora in America has an anchor institution in Washington. The Chinese have the Smithsonian's National Museum of Asian Art, Jewish Americans have the United States Holocaust Memorial Museum, African Americans have an entire wing of the National Mall. Indian Americans — roughly five million strong, the highest-earning ethnic group in the country, and increasingly visible in corporate boardrooms and Congressional corridors — have nothing.

Dr Amitabh Sharma wants to change that, and he has spent the better part of a decade quietly laying the groundwork.

## A Building, a Pitch, and Eight Years of Planning

Sharma, an Atlanta-based educationist and community leader, is the driving force behind the India Heritage Centre, a proposed 20,000-square-foot museum that would be the first dedicated institution in the United States focused exclusively on India's civilisational, cultural, and historical arc — spanning, as its organisers put it, more than eleven thousand years.

The project is not a concept sketch. Over eight years, Sharma has consulted indologists, historians, and archaeologists to validate the content. He has assembled a plan for ten galleries covering the Indus Valley Civilisation, India's scientific innovations, spiritual traditions, the independence movement, colonial resistance, and the country's modern rise. The museum would deploy immersive technology, virtual reality, augmented reality, interactive exhibits, and multimedia displays to present India's contributions to a global audience.

Now he has made a concrete ask. Sharma has approached the Indian Embassy in Washington for the use of a building it purchased in 2013, situated in the heart of the American capital. If that arrangement does not materialise, the India Heritage Centre is prepared to purchase land on its own.

"At a time when narratives shape global perception, future generations require authentic institutions that preserve, present, and celebrate India's extraordinary contributions to humanity," Sharma told PTI.

## Why It Matters to the Diaspora

The museum is not pitched as a vanity project or a diplomatic showcase. Its stated primary audience is the younger generation of Indian Americans — second- and third-generation kids who grow up with a foot in two worlds and often lack a physical, curated space that tells them where they came from.

"Indian history and Indian civilisation has never been portrayed in the strength that it deserves," Sharma has said in multiple interviews. "It is important to tell the world about the rich civilisation, heritage and contributions that India has made."

That framing resonates at a moment when the Indian American community is grappling with questions of identity, representation, and rising hate. The FBI's latest data showed anti-Hindu and anti-Sikh hate crimes at record highs. A Carnegie Endowment survey earlier this year found that seventy-one per cent of Indian Americans disapprove of the country's direction, and a striking forty per cent are considering leaving the United States entirely. Against that backdrop, an institution that asserts cultural pride while educating mainstream Americans feels less like a luxury and more like a necessity.

## The Numbers

The India Heritage Centre estimates the total project cost at between twelve and fourteen million dollars. Funding would come from high-net-worth individuals, corporate sponsorships, grants, crowdfunding, and community support. A similar museum is also planned for Atlanta, with other locations under consideration.

The ten proposed galleries would map a narrative from the Indus Valley to a "futuristic global leadership vision," with a 350-seat auditorium for lectures and discourse, a library, reception facilities, and a gift centre.

## What Comes Next

The project faces the usual hurdles of diaspora-funded cultural institutions: real estate in Washington is brutally expensive, and rallying millions of dollars from a community that is generous but not always coordinated requires sustained leadership. The embassy route, if it works, would solve the real-estate problem at a stroke. If it does not, the timeline stretches.

But the ambition is clear. India's diaspora has built temples, endowed university chairs, and funded hospital wings across America. A museum that tells the full civilisational story — not as an embassy brochure but as a proper cultural institution — would be something new. Whether Sharma can pull it off will depend on how many Indian Americans agree that the story is worth fourteen million dollars to tell.

For a community that has spent decades proving its economic worth, the museum poses a different kind of question: what does it mean to be remembered?"""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One Hundred and Fifty Dancers, Seventeen Countries, Three Nights Under the Acropolis: Inside the World Festival of Indian Dance",
        "subheadline": "The fourth edition of the UNESCO-endorsed classical Indian dance festival opens in Athens this week, with performers from the United States, Canada, Britain, Oman, South Africa, and a dozen other nations gathering at the foot of Western civilisation's most famous monument.",
        "slug": make_slug("world-festival-indian-dance-athens-acropolis-2026"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Indian classical dance traditions carried and performed by diaspora communities across 17 countries, showcasing how NRIs preserve and project cultural heritage on a global stage",
        "tags": ["nri", "diaspora", "dance", "bharatanatyam", "athens", "culture", "UNESCO", "classical-dance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "CID Events (International Dance Council at UNESCO)", "url": "https://events.cid-world.org/4th-world-festival-of-indian-dance-2026/"},
            {"name": "AllEvents.in", "url": "https://allevents.in/athens/4th-world-festival-of-indian-dance/80002852754959"},
            {"name": "GoGetFunding (Subashni Naicker campaign)", "url": "https://gogetfunding.com/performance-at-4th-world-festival-of-indian-dance/"},
            {"name": "This Is Athens (Official Athens Guide)", "url": "https://www.thisisathens.org/events/9th-bollywood-and-multicultural-dance-festival"}
        ]),
        "score_total": 75,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Bharatanatyam_dance_performance_at_the_Khajuraho_Dance_Festival_2026_009.jpg/1280px-Bharatanatyam_dance_performance_at_the_Khajuraho_Dance_Festival_2026_009.jpg",
        "image_caption": "A Bharatanatyam dancer performing at the Khajuraho Dance Festival earlier in 2026",
        "image_attribution": "Wikimedia Commons",
        "body": """There is something quietly radical about performing a Bharatanatyam margam at the foot of the Acropolis. Two civilisations that independently invented theatre, philosophy, and the idea that dance could be sacred — meeting on a hillside in Athens while the Parthenon glows overhead.

That is exactly what is happening this week. The 4th World Festival of Indian Dance opened on July 13 at the Dora Stratou Theatre on Philopappou Hill, directly opposite the Acropolis, and runs through July 15. Over a hundred and fifty dancers from at least seventeen countries are performing classical Indian dance — and only classical Indian dance — on one of Europe's most storied stages.

## The Diaspora Dances

The festival, endorsed by the International Dance Council (CID) at UNESCO and organised by the Dora Stratou Dance Theatre, which has operated for seventy-three years, is now in its fourth edition. Last year's festival drew 129 dancers from thirteen countries who presented forty-six performances. This year's roster is larger and more geographically scattered.

The participant list reads like a census of the Indian diaspora's cultural footprint. Dancers are arriving from the United States, the United Kingdom, Canada, Oman, India, Germany, Portugal, South Africa, Bangladesh, Hungary, Australia, the Netherlands, Singapore, the United Arab Emirates, Austria, Poland, and Italy. Many are children and teenagers — second-generation diaspora kids who learn Bharatanatyam, Kathak, Kuchipudi, or Odissi at weekend classes in New Jersey or suburban London, and are now performing on a UNESCO-endorsed international stage.

The rules are strict. Only classical Indian dance forms are permitted: Bharatanatyam, Kathak, Kathakali, Kuchipudi, Manipuri, Mohiniyattam, Odissi, Sattriya, and their sub-traditions. Performers must be registered with CID, the global dance body at UNESCO. Soloists get five minutes; companies receive more. There is no Bollywood, no fusion, no contemporary reinterpretation. The festival is, by design, a purist's showcase.

## From Muscat to Athens

What is striking about the roster is where the dancers come from — and who they are. A significant contingent, more than two dozen performers, hails from Oman, reflecting the deep roots of Indian classical dance in Gulf diaspora communities where families have maintained guru-shishya traditions across generations. Several performers are listed from the United States, including dancers from schools in New Jersey, California, and the Midwest.

One of the more moving backstories belongs to Subashni Naicker, a South African Bharatanatyam dancer who launched a crowdfunding campaign to finance her trip to Athens. "This is more than a performance," she wrote in her appeal. "It is an opportunity to carry not only my art, but my heritage, my teachers' blessings, and my country's spirit with me."

That sentiment captures the festival's deeper significance. Classical Indian dance, with its rigorous training requirements and ancient pedagogical structures, is one of the hardest cultural traditions to sustain in diaspora. Unlike Bollywood dance, which travels easily through cinema and social media, forms like Bharatanatyam and Kathak demand years of training under a qualified guru, regular practice, and live performance. The fact that families in Oman, Hungary, and suburban Toronto are investing in this tradition — and that their children can then perform under the Acropolis — says something about the resilience of Indian cultural transmission abroad.

## A Stage Worth the Symbolism

The Dora Stratou Theatre is no ordinary venue. The open-air amphitheatre sits on Philopappou Hill, in the shadow of the Acropolis, and has hosted traditional dance performances for more than seven decades. Its choice as the home for an Indian classical dance festival is deliberate. The organisers describe it as "a most illustrious venue — under the Acropolis of Athens, cradle of Western civilisation."

The symbolism works both ways. Greece and India share long historical connections — from Alexander's encounter with Indian philosophers to the Gandhara school of art that fused Hellenistic and Buddhist aesthetics. A festival that places Odissi and Kathakali on the same hillside where Sophocles once staged tragedies is making a quiet argument about civilisational parity.

## What the Festival Signals

For the Indian diaspora, the Athens festival is a small but significant data point in a larger trend. Classical Indian arts — dance, music, Sanskrit theatre — are finding international institutional homes, not just community-hall stages. UNESCO endorsement lends formal recognition. The Dora Stratou's seventy-three-year pedigree lends prestige. And the growing number of participating countries, from thirteen to seventeen in a single year, suggests momentum.

None of which would matter if the performances were not any good. But that is precisely the point of insisting on classical forms only. The festival is betting that Bharatanatyam under the Acropolis does not need a Bollywood remix to hold an audience. Three nights in Athens will tell whether the bet pays off."""
    }
]

for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
