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

stem_body = """When the third National STEM Festival opens in Washington this week, the program of finalists will read, in places, like the membership roll of a Telugu or Tamil association picnic. Of the 55 middle- and high-school students named 2026 National STEM Champions, at least 24 are of Indian origin — a share that no longer surprises anyone who follows these competitions, and which says as much about the diaspora's second generation as it does about American science education.

## A pattern, not a fluke

The numbers are striking on their own. Fewer than 5% of applicants are selected as Champions, a tighter filter than many elite universities apply. That nearly half the cohort traces its roots to a single country of origin — one that supplies roughly 1.5% of the U.S. population — is the sort of statistic that gets mistaken for an accident. It is not.

The projects themselves resist the cliché of the precocious child building a baking-soda volcano. Haritaa Ramesh of San Ramon, California, built a low-cost device, VeinViewer, to make veins visible for blood draws. Shripriya Kalbhavi of San Jose worked on the genetic code behind ALS. Diya Ramakrishnan of Saginaw, Michigan, developed a mixed-reality app to guide surgeons through pancreatic-cancer operations. Antariksha Sharma of Fairfield, Iowa, is trying to detect Alzheimer's from a teardrop. These are not science-fair dioramas; several are patent-pending.

## The machinery behind the medals

The diaspora's dominance in academic competitions — the Scripps Spelling Bee, where Indian-American children have won 30 of the last 36 titles, is the most famous example — is often explained away with lazy shorthand about "tiger parenting." The reality on display at events like the STEM Festival is more interesting. It is a community that has built an entire parallel infrastructure of coaching circles, weekend enrichment classes, and older students mentoring younger ones, layered on top of households where a parent is frequently an engineer or physician who can debug a circuit at the kitchen table.

It is also a community acutely aware that its foothold in America was won through education and skilled work, and that the path it took — the H-1B visa, the graduate degree, the research lab — is the one it most trusts to secure the next generation. The children competing this week are, in a sense, running the family playbook forward.

## What the festival actually offers

Each Champion, with a guardian, receives an expenses-paid trip to Washington to present their work to leaders from business, government and academia, culminating in a free public Build Day expo on June 27. For families that have spent years ferrying children to robotics clubs and olympiad practice, the festival is less a finish line than a credentialing event — a place where a teenager's project gets seen by the people who fund laboratories and write recommendation letters.

The geographic spread of the 2026 Indian-American Champions is its own quiet story. They come not just from the coastal tech enclaves but from Grand Forks, North Dakota; Rapid City, South Dakota; Onalaska, Wisconsin; Morgantown, West Virginia. The diaspora's STEM culture, in other words, has diffused well past Silicon Valley and Edison, New Jersey, into towns where an Indian family might be one of a handful.

## The uncomfortable subtext

There is a less comfortable conversation underneath the celebration. The same families producing these Champions are watching the political mood around high-skilled immigration sour, and a recent Carnegie survey found that a striking share of Indian Americans have at least thought about leaving the United States. The students inventing carbon-capture materials and cancer-diagnostic tools this week represent precisely the human capital that debate is ostensibly about. Whether America retains them — whether the next VeinViewer gets commercialized in Boston or Bangalore — is a question the festival's organizers cannot answer, and one the diaspora is increasingly asking aloud.

For now, though, the achievement stands on its own terms. Two dozen children of immigrants, many of them the first in their American-born line, will spend the last week of June showing the country's decision-makers what they have built. The diaspora has long argued that its contribution to the United States is measured in more than remittances and tax receipts. This week, that argument has 24 names attached to it."""

mahotsav_body = """For two days at the end of June, a community hall in Wembley will fill with the sound of Kolkata — the cadence of Bengali theatre, the thrum of a tabla, the smell of biryani that organizers have flown in from one of the city's most famous kitchens. London Mahotsav, now in its third edition, bills itself as the largest cultural gathering of Bengali Indians in the United Kingdom. It is also a small case study in how a diaspora preserves a regional identity that, even within India, can feel like a minority concern.

## Bengal, rebuilt in Wembley

The festival takes place on June 27 and 28 at the Sattavis Patidar Centre in Wembley Park, a venue better known for Gujarati community events — a detail that itself captures something about how Indian diaspora spaces get shared and repurposed. Over two days the program runs through live music, debate, drama, literature, fashion and cinema, the cultural diet of an educated Bengali middle class transplanted some 5,000 miles from home.

The organizers have leaned into the specifics rather than diluting them for a general audience. Performers are drawn from Kolkata itself, and the food billing makes a point of importing Aminia, a biryani institution in the city. The bet is that authenticity, not broad accessibility, is what draws a crowd willing to give up a summer weekend.

## Why a regional festival, in a sea of pan-Indian ones

Britain's Indian diaspora is overwhelmingly associated, in the public imagination, with Punjabi and Gujarati communities — the corner shops, the gurdwaras, the Diwali lights on Leicester's Belgrave Road. Bengalis, who in Britain are often conflated with the much larger Bangladeshi-Bengali population, occupy a quieter cultural niche. A festival like London Mahotsav is partly an act of insistence: that the Bengali strand of Indianness, with its distinct literature, its Durga Puja calendar, its particular reverence for Tagore and adda — the untranslatable art of the long, meandering conversation — deserves its own stage.

That insistence matters most for the second generation. For children growing up in London with a Bengali surname and a London accent, a festival is one of the few places where the language is not just spoken at home but performed, celebrated and treated as something worth dressing up for. The fashion segment and the youth-oriented programming are not incidental; they are the mechanism by which a culture tries to make itself attractive to people who could just as easily let it lapse.

## The economics of cultural memory

Events like this one survive on a delicate economy. Ticket sales, sponsorship and trade stalls fund a program whose real product is intangible — a weekend in which Bengaliness feels central rather than peripheral. The festival actively courts sponsors and vendors, and its growth from a one-off to an annual, multi-day fixture suggests the model is working. Each edition imports performers and culinary names from Kolkata, an arrangement that keeps the diaspora event tethered to the source culture and gives artists back home a lucrative overseas circuit.

## A familiar diaspora arithmetic

London Mahotsav sits within a broader pattern visible across the Indian diaspora this summer, from Telugu conventions filling American arenas to DesiFest taking over downtown Toronto. The diaspora is rich enough, settled enough and self-aware enough to fund the elaborate reproduction of its regional cultures abroad — and anxious enough about assimilation to feel it must.

What distinguishes the Bengali version is its bookishness. This is a culture that measures itself in literature and argument as much as in dance and food, and a festival that programs debate alongside biryani is being true to that temperament. Whether the third edition draws a bigger crowd than the last is, in the end, beside the point. The festival's real function is to give a dispersed community a fixed date in the calendar — a weekend when, in a hall in Wembley, it is once again unambiguously at home."""

aapi_body = """The American Association of Physicians of Indian Origin will gather this June in Tampa for its 44th annual convention, and the organization's own description of itself doubles as a statement about the diaspora's place in American life. AAPI now represents more than 120,000 Indian-American physicians across 130 local chapters — roughly 10% of all doctors in the United States, and close to half of its international medical graduates. By its reckoning, an Indian-origin physician treats every seventh patient in the country.

## A convention, and a reckoning

The Tampa meeting, held at the JW Marriott and Marriott Water Street hotels on the city's waterfront, carries the usual machinery of a large professional gathering: continuing-education credits, scientific sessions, leadership seminars, a trade exhibition where pharmaceutical companies pay $10,000 a booth to reach an audience of department heads and hospital executives. This year's program leans hard into physician wellness — yoga, meditation, "healing the healers" — a theme that reflects a profession wrestling with burnout as much as a community reconnecting with its cultural roots.

But the convention convenes against a sharper backdrop than usual. AAPI has spent the spring in an unaccustomed role: that of a political combatant defending the very immigration pathway that built it.

## The $100,000 question

Earlier this year, the association publicly welcomed a court ruling that blocked a proposed $100,000 requirement on H-1B physician visa applications — a policy AAPI argued would have fallen hardest on rural hospitals, safety-net institutions and underserved communities that depend disproportionately on foreign-trained doctors.

"This ruling restores fairness and stability to a system that thousands of international physicians depend upon," said Dr. Amit Chakrabarty, AAPI's president. "This is not a political victory — it is a healthcare victory."

The framing is careful, but the stakes are not abstract. International medical graduates — physicians trained outside the United States and Canada — are a structural feature of American healthcare, not a marginal supplement. Had the fee survived, AAPI warned, hospitals would have withdrawn job offers, vacancies would have gone unfilled, and wait times in already-stretched regions would have lengthened. The organization that began in 1982 as a networking body for immigrant doctors now finds itself functioning, of necessity, as a lobby.

## From arrival to influence

The arc is a familiar diaspora story compressed into four decades. The Indian physicians who came to the United States in the 1970s and 1980s, many to staff hospitals in towns American-trained doctors avoided, were filling a gap. Their children went into medicine, law, technology and increasingly politics. The institution they founded to swap referrals and ease isolation now develops health-policy agendas and "encourages legislative priorities," in the bland phrasing of its officers — the language of an establishment, not an outsider.

That transition is visible in the convention's guest list and programming, which mix scientific assemblies with cultural showcases, yoga gurus with health-policy panels. A dedicated day for young physicians and medical students — the AAPI YPS-MSRF Day — signals an organization thinking about succession, about the residents and trainees who will inherit both its influence and its fights.

## The diaspora's most quietly powerful institution

For all the attention paid to Indian-American CEOs and politicians, AAPI may be the diaspora's most consequential professional body, precisely because its members' work is so woven into ordinary American life. A patient in a Florida emergency room or a Kentucky clinic is statistically likely to be treated by one of its members, whatever they know of the organization's name.

That ubiquity is the source of both its confidence and its current anxiety. The community that staffs one in seven American patient encounters has earned a seat at the policy table — but the same political currents that produced the H-1B fee proposal suggest the pathway that created AAPI is no longer something the diaspora can take for granted. When the physicians convene in Tampa, the meditation sessions and the cuisine will share the agenda with a more pointed question: how to defend the system that let them arrive, for the doctors who hope to follow."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "Half of America's Top Young Inventors This Year Share One Country of Origin. It Isn't a Coincidence.",
        "subheadline": "At least 24 of the 55 students named 2026 National STEM Champions are of Indian origin. Their projects — and their hometowns — say a lot about the diaspora's second generation.",
        "slug": make_slug("national-stem-festival-2026-indian-american-champions-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Nearly half of America's most elite young STEM honorees are children of Indian immigrants, showcasing how the diaspora's education-first culture is reproducing itself in the second generation — even as the high-skilled immigration pathway that brought their parents comes under political pressure.",
        "tags": ["nri", "diaspora", "indian-american", "stem", "education", "second-generation"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "American Bazaar — 24 Indian American Students Named 2026 National STEM Champions", "url": "https://americanbazaaronline.com/2026/03/31/24-indian-american-students-named-2026-national-stem-champions-477899/"},
            {"name": "National STEM Festival (EXPLR)", "url": "https://nationalstemfestival.org/"},
            {"name": "Madhyamam — Indian American teen wins 2026 Scripps National Spelling Bee", "url": "https://www.madhyamamonline.com/"}
        ]),
        "score_total": 78,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/9242846/pexels-photo-9242846.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Teenagers collaborate on a robotics project in a laboratory setting",
        "image_attribution": "Pexels",
        "body": stem_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "One in Seven American Patients Sees a Doctor of Indian Origin. Now Their Association Is Fighting to Protect the Pipeline.",
        "subheadline": "As 120,000-strong AAPI convenes in Tampa for its 44th convention, a victory over a $100,000 visa fee shows how the diaspora's doctors became a political force.",
        "slug": make_slug("aapi-44th-convention-tampa-indian-physicians-h1b-visa-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The American Association of Physicians of Indian Origin is arguably the diaspora's most consequential professional body — its members treat one in seven US patients — and its recent fight against a $100,000 H-1B physician visa fee shows a community defending the very immigration pathway that built it.",
        "tags": ["nri", "diaspora", "indian-american", "physicians", "aapi", "h1b", "healthcare"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — AAPI's 44th Annual Convention", "url": "https://theindianeye.com/"},
            {"name": "AAPI Convention 2026 (official)", "url": "https://www.aapiconvention.org/"},
            {"name": "India Tribune — AAPI Announces 44th Annual Convention in Tampa", "url": "https://www.indiatribune.com/"}
        ]),
        "score_total": 76,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/8460371/pexels-photo-8460371.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A diverse group of healthcare professionals in a clinical setting",
        "image_attribution": "Pexels",
        "body": aapi_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "A Slice of Kolkata Lands in Wembley This Weekend — Right Down to the Imported Biryani",
        "subheadline": "London Mahotsav, Britain's largest Bengali-Indian cultural gathering, returns for a third year. It's a quiet lesson in how a diaspora keeps a regional identity alive.",
        "slug": make_slug("london-mahotsav-2026-bengali-diaspora-uk-cultural-festival"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Bengalis are a quieter strand of Britain's Punjabi- and Gujarati-dominated Indian diaspora, and London Mahotsav is an act of insistence that their distinct culture — bookish, literary, Tagore-revering — deserves its own stage, especially for a London-raised second generation at risk of letting it lapse.",
        "tags": ["nri", "diaspora", "uk", "bengali", "culture", "festival", "london"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "London Mahotsav 2026 (official)", "url": "https://www.londonmahotsav.co.uk/"},
            {"name": "Asian Voice — UK Indian community coverage", "url": "https://www.asian-voice.com/"}
        ]),
        "score_total": 68,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36121661/pexels-photo-36121661.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Bharatanatyam dancer in traditional attire performs a classical Indian dance on stage",
        "image_attribution": "Pexels",
        "body": mahotsav_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
