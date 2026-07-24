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

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "On the Same Saturday, Two Sikh Parades Shut Down Streets 1,200 Miles Apart. Neither Was an Accident.",
        "subheadline": "From a small Oregon city to a British Columbia mountain town, the Nagar Kirtan has become the diaspora's most visible — and most deliberate — act of public belonging.",
        "slug": make_slug("sikh-nagar-kirtan-parades-salem-squamish-diaspora-public-faith"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Sikh families abroad, the Nagar Kirtan is both an act of faith and a calculated answer to decades of being mistaken for strangers in their own towns — a once-a-year invitation to neighbours who otherwise never step inside a gurdwara.",
        "tags": ["nri", "diaspora", "sikh", "community", "canada", "usa"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Salem Statesman Journal", "url": "https://www.statesmanjournal.com/story/news/2026/06/18/sikh-parade-to-march-through-salem-streets-june-20/"},
            {"name": "The Squamish Reporter", "url": "https://www.squamishreporter.com/2026/06/15/squamish-community-invited-to-annual-sikh-parade-on-june-20/"},
            {"name": "The Pluralism Project, Harvard University", "url": "https://pluralism.org/sikh-parade-extols-peace"}
        ]),
        "score_total": 72,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/8/89/Sikh_Freedom_Parade_and_Festival_SF_Civic_Center_2018-06-10.jpg/1280px-Sikh_Freedom_Parade_and_Festival_SF_Civic_Center_2018-06-10.jpg",
        "image_caption": "Participants in a Sikh Nagar Kirtan procession and festival at San Francisco's Civic Center",
        "image_attribution": "Wikimedia Commons",
        "body": """In Salem, Oregon, on Saturday, parts of Commercial and 12th streets belonged for five hours to a slow-moving river of orange and blue. In Squamish, British Columbia, a mountain town of fewer than 25,000, a procession set out from the Gurdwara Sahib at half past ten and wound through five named streets before ending at a waterfront pavilion. The two events sat 1,200 miles apart and were organised by people who have likely never met. They happened on the same day for the same reason.

June marks the martyrdom of Guru Arjan Dev Ji, the fifth of the ten Sikh Gurus, tortured to death by Mughal authorities in 1606. The Nagar Kirtan — literally "town hymn-singing" — is how Sikhs commemorate it: a procession behind the Guru Granth Sahib, the holy scripture, accompanied by the singing of shabads and demonstrations of Gatka, the martial art of the Khalsa. It is among the oldest public rituals the faith has. What is newer is the role it now plays for a community scattered across North America.

## A procession that doubles as an introduction

The Salem parade, hosted by the Dasmesh Darbar Sikh Temple, was its 21st. Organisers expected between 1,200 and 1,500 participants — a substantial turnout for a city of 180,000. In Squamish, the Sikh Society anticipated more than 8,000 attendees, a figure that dwarfs the town's South Asian population several times over and tells you the audience is meant to be everyone else.

That is the quiet design of the modern Nagar Kirtan. Langar — the free communal meal that is a pillar of Sikh practice — is served to all comers regardless of faith, caste or background. In Squamish, roughly 26 food stalls lined the route. The dignitaries invited were not temple elders but the mayor, the local MLA and MP, the RCMP and representatives of the Squamish Nation. Paramjit Sidhu, the society's vice-president, framed the day in plain terms: "For me, this is basically teaching about spirituality, and it's about human rights. Our fifth Guru made us understand that everybody has the right to live on this planet, free."

## The unspoken second purpose

There is a reason a religious procession leans so hard into outreach, and the community rarely says it aloud at the microphone. Sikhs in North America have spent decades being misidentified. After September 2001, turbaned men were assaulted by attackers who could not distinguish a Sikh from the people they imagined they hated; the first person killed in a post-9/11 hate crime was a Sikh gas-station owner in Arizona. Two decades on, surveys still find that most Americans cannot correctly identify the turban as a Sikh article of faith.

The Nagar Kirtan answers that gap not with a press release but with a plate of food. As one Bay Area temple president put it years ago, when the Sikh Center of the San Francisco Bay Area first turned the holiday into a community party: "America has gone from a Christian country to the most diverse nation in the world. The education hasn't kept up." The procession is the curriculum.

## Faith that travels with the family

For the diaspora, the parade carries a private weight alongside the public one. A second-generation Sikh child in Squamish or Salem grows up fluent in a culture that does not, by default, know what a gurdwara is. The annual march is one of the few days a year when that child sees their grandfather's faith occupy a main street rather than a side room — when the langar hall spills out onto public asphalt and the wider town shows up to eat.

The Squamish event nearly didn't happen. Last year's parade was cancelled when the Dryden Creek wildfire forced the town's attention elsewhere. Sidhu said the 2026 turnout was buoyed by "pent-up enthusiasm" after the gap — a reminder that these rituals, once interrupted, are missed.

What both processions demonstrated this weekend is how thoroughly a Punjab-rooted observance has localised. The route in Salem bends around a recreation field; the one in Squamish ends at a pavilion named in the Squamish Nation's language. The hymns are the same ones sung 400 years ago. The streets are entirely new. For a diaspora that lives between two worlds, that is rather the point: the faith does not ask its members to choose. It simply asks the town to come and eat."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Buying a Flat in India Has Long Been a Compliance Nightmare for NRIs. Delhi Just Promised to Fix It.",
        "subheadline": "From October, a PAN-based system is set to replace the tangle of TAN registrations and non-resident withholding rules that turn an ordinary property purchase into a paperwork ordeal.",
        "slug": make_slug("nri-property-purchase-pan-system-tds-compliance-easing-october"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "Millions of NRIs own or plan to buy property in India, and the rules differ sharply depending on whether the person across the table is a resident or a fellow non-resident — a distinction most buyers discover only when the transaction is already half-done.",
        "tags": ["nri", "diaspora", "property", "tds", "fema", "finance"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "Outlook Money", "url": "https://www.outlookmoney.com/nri/nri-property-purchase-why-the-sellers-residential-status-matters"},
            {"name": "Mondaq — Citizenship Amendment Rules 2026", "url": "https://www.mondaq.com/india/general-immigration/citizenship-amendment-rules-2026"}
        ]),
        "score_total": 70,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/35114454/pexels-photo-35114454.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
        "image_caption": "A residential apartment building in Bengaluru, India",
        "image_attribution": "Pexels",
        "body": """Ask any non-resident Indian who has bought a flat back home in the past few years, and somewhere in the story is a moment of dawning horror at a tax counter. The price was agreed. The loan was arranged. And then the question arrived: was the seller a resident, or another NRI? Because depending on the answer, the buyer's obligations could swing from trivial to onerous — and getting it wrong could mean a penalty notice years later.

India's government now says relief is coming. From 1 October 2026, officials plan to introduce a simpler, PAN-based system for property purchases involving non-resident sellers, broadly aligning them with how resident-seller deals already work. For the diaspora, it is one of the more consequential pieces of housekeeping in years — even if it arrives wrapped in the language of tax administration rather than fanfare.

## Why the seller's status matters so much

The trap lies in India's tax-deducted-at-source regime. When an NRI buys property from a *resident* seller and the value exceeds ₹50 lakh, the buyer must deduct 1% TDS and deposit it. Straightforward enough — and crucially, no TAN, the Tax Deduction Account Number, is required.

Flip the seller's status, however, and the machinery changes entirely. When the seller is themselves an NRI, the buyer must obtain a TAN, deduct tax under the more demanding non-resident withholding rules, deposit it, file TDS returns, and issue a Form 16A to the seller. "It can take a real bite out of the transaction," one tax adviser noted — not in money so much as in time, professional fees and the sheer risk of error for a buyer who may be sitting in New Jersey or Dubai trying to manage all of it remotely.

This is the burden the October change is meant to lift, by moving non-resident-seller transactions onto the same PAN-based footing as resident deals.

## The part that is already simpler than people fear

For all the anxiety around TDS, the foreign-exchange side of NRI property ownership is relatively benign. Under the Foreign Exchange Management Act (FEMA), non-resident Indians can freely buy residential or commercial property in India with no real restrictions on quantity or location. Overseas Citizens of India (OCI) cardholders enjoy the same economic parity.

The hard limits are narrow but absolute. NRIs and OCI holders cannot buy agricultural land, plantation property or farmhouses — full stop, regardless of how the purchase is funded. "Beyond that, it's just the usual due diligence — checking the title, ownership history, and tax paperwork — before you go ahead and close the deal," the adviser said.

## A wider tidy-up of NRI rules

The property change does not arrive in isolation. India has spent the past year quietly modernising the legal scaffolding around its diaspora. The Citizenship Amendment Rules of 2026 introduced electronic OCI registration — an "e-OCI" that exists as a digital government record rather than a physical booklet, allowing real-time updates for immigration and border control. The Immigration and Foreigners Amendment Order, published on 18 June, formally wrote the term "OCI Cardholder" into immigration regulation and aligned its definition with the Citizenship Act.

Taken together, the moves point in one direction: a state trying to make it administratively easier to be Indian from abroad. That matters because the diaspora's financial relationship with India is enormous and growing — remittances, NRI deposits and property all feed a flow of capital that Delhi increasingly courts rather than merely tolerates.

## What buyers should still watch

The October system is a plan, not yet a finished rulebook, and the details will determine how much friction actually disappears. Until it takes effect, the old distinction stands: confirm the seller's residential status *before* agreeing terms, not after. An NRI seller still triggers the TAN-and-withholding chain, and a buyer who skips it inherits the liability.

The deeper lesson for the diaspora is an old one. Owning a piece of home from afar has always carried a tax of attention — the forms, the statuses, the rules that change with a budget speech. Delhi is now offering to lower that tax. For the millions who have stared blankly at a TDS counter while a property deal hung in the balance, October cannot come soon enough."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Two Indian-Origin Students Pitched the Impossible in Under Two Minutes. They Walked Out of Purdue With the Top Prize.",
        "subheadline": "At a campus ideation contest built to reward big swings, second-generation names dominated the winners' list — a small data point in a much larger story about who is doing America's frontier thinking.",
        "slug": make_slug("purdue-moonshot-pitch-challenge-indian-origin-students-diaspora-stem"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The children of Indian immigrants are quietly over-represented at the inventive edge of American campuses — and contests like this one show the pipeline running not through famous founders but through 19-year-olds pitching space-based solar power between classes.",
        "tags": ["nri", "diaspora", "stem", "students", "purdue", "innovation"],
        "urgency": "low",
        "sources": json.dumps([
            {"name": "The Indian Eye", "url": "https://theindianeye.com/indian-origin-students-win-big-at-purdues-moonshot-pitch-challenge/"},
            {"name": "Purdue University", "url": "https://www.purdue.edu/"}
        ]),
        "score_total": 64,
        "status": "review",
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c5/Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg/1280px-Frederick_L_Hovde_Hall_of_Administration_Purdue_University_2016_01.jpg",
        "image_caption": "Frederick L. Hovde Hall of Administration at Purdue University in West Lafayette, Indiana",
        "image_attribution": "Wikimedia Commons",
        "body": """The rules of Purdue University's Moonshot Pitch Challenge are almost cruelly simple. You get two minutes. In that window you must explain a real-world problem and propose a solution big enough to justify the contest's name. There are no slides to hide behind and no second chances. This year, when the judges in West Lafayette, Indiana finished tallying, two of the standout names belonged to students of Indian origin.

Suryansh Panwar, an applied statistics student in the College of Science, was on the team that took first place in the Moonshot category — the bracket reserved for "seemingly impossible" problems — and also won Best Pitch. Their venture, Empyrean Energy, proposed harvesting solar power in space and beaming it down for continuous, zero-emission energy on Earth. Ayush Karkare, in Purdue's First-Year Engineering program, was part of the team that won the Earth category with BioVolt, a biophotovoltaic panel that generates electricity through photosynthesis while pulling carbon out of the air. First-place teams in each of the three categories took home $1,500.

## Two minutes, no slides

What makes Moonshot revealing is its format. Stripped of polish, a pitch competition becomes a test of clarity under pressure — the ability to make a stranger care about an idea before a timer runs out. "Giving the pitch in two minutes was difficult, but our focus was mainly on providing quality," Panwar said afterward, adding that he intends to enter Purdue's new-venture challenge next semester. Karkare was blunter about the cost: "It took a lot of effort to present; I practiced for hours and hours."

The contest sorts ideas into three buckets — Earth, for socioeconomic problems; Orbit, for company-building; and Moonshot, for the genuinely audacious. Students across every Purdue college submitted video pitches. That a first-year engineering student and an applied-statistics undergraduate ended up on the winning teams says something about how early the inventive impulse now surfaces.

## A pattern, not a coincidence

One campus contest proves nothing on its own. But set it beside the rest of the season and a pattern emerges. This year's Scripps National Spelling Bee went to Shrey Parikh, the 31st champion of Indian heritage in the last 37 editions. Of the 126 Sloan Research Fellowships awarded to the most promising early-career scientists in the United States and Canada, a striking share went to Indian-American researchers in cryptography, statistics, mathematics and neuroscience. The names recur — in pitch finals, in fellowship cohorts, in spelling-bee brackets — with a regularity that has stopped surprising anyone who watches American higher education.

The diaspora's children are not over-represented at the top of these contests by accident. They are, disproportionately, the offspring of a particular kind of immigrant: engineers, doctors and academics who arrived on skilled visas and built households where the expectation of intellectual effort was simply ambient. The Moonshot winners are a generational echo of that arrival — second-generation students treating frontier problems as ordinary homework.

## The quieter significance

For the families behind these students, a $1,500 cash prize is beside the point. The significance is that a kid whose parents may have landed in America with two suitcases and a graduate-school admission is now standing in front of judges proposing to put solar arrays in orbit — and being taken seriously. That is the diaspora story in miniature: not one famous CEO, but a steady stream of young people moving from the margins of a country's imagination toward its centre.

It is worth resisting the urge to flatten this into a tidy narrative of inevitable success. Plenty of these students will graduate into a tighter, more anxious America, where the visa pathways their parents used are narrower and the political mood toward foreign-born talent is sourer. The Moonshot finalists are entering a country in the middle of an argument about exactly the kind of skilled immigration that produced them.

But for one afternoon in Indiana, none of that was on the clock. There were two minutes, an impossible problem, and a pair of students who had practised for hours and hours. They made the room believe the impossible was worth funding. For a community that has spent two generations betting on exactly that proposition, it was a familiar kind of win."""
    }
]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
