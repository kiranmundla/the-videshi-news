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

article1_body = """A community organization rarely measures its life in decades. Most flare up around a single grievance or festival and quietly fold once the volunteers tire. So when the Connecticut chapter of the Global Organization of People of Indian Origin (GOPIO-CT) marked its twentieth year on June 13 at the Water's Edge Banquet Hall in Darien, the milestone said as much about staying power as about the five honorees on stage.

The chapter chose to celebrate not with self-congratulation but with a roster that doubled as a map of where the diaspora has reached. A sitting state senator. A nanotechnology executive. A 174-year-old bank's new chief executive. A journalist of three decades. An engineering professor of nearly forty years. The breadth was the point.

## A Map of Arrival

State Senator Sujata Gadkar-Wilcox, honored for political leadership, was elected to represent Connecticut's 22nd District in 2024 while continuing to teach legal studies at Quinnipiac University. Her acceptance speech refused the easy register of gratitude. She spoke instead about who gets to claim the country.

"Sunday family dinners have their roots in Italian culture," she said. "Similarly, when Quinnipiac University hosts a Garba dance and Diwali celebration, students from different backgrounds mark their calendars. These traditions become part of the American story because immigrants and their families are the American story." Alluding to a recent wave of anti-immigrant posts online, she added that the deeper problem was "who gets to say they're truly American, and who has to justify their story."

The other awardees filled in the professional spectrum. Dr. Anil R. Diwan, founder and executive chairman of the Connecticut-based, NYSE-listed NanoViricides, was recognized for entrepreneurship; his firm develops antiviral therapies that aim to neutralize viruses mechanically. Nitin Mhatre, who became chief executive of First County Bank in April, took the corporate leadership award for steering an independent mutual community bank that has operated in Fairfield County for more than 174 years. Hemchandra Shertukde, a University of Hartford engineering faculty member of nearly four decades, was honored for applied sciences. Veteran journalist Ajay Ghosh, founder of the Indo-American Press Club, accepted the journalism award with a warning that "journalism is facing a crisis as never before" — a strain he called "global and systemic."

## The Institutional Habit

What separates a chapter that lasts from one that does not is, mostly, the unglamorous habit of showing up. GOPIO-CT's founder members and a long line of past presidents were recognized alongside the honorees — Dr. Thomas Abraham, the chapter's founders, and presidents who had each carried the organization through its quieter years.

Abraham, who is also founder president of GOPIO International, argued that the Connecticut chapter had become a template. "In many ways, its success became a model for GOPIO International in shaping the structure and activities of local chapters worldwide," he said. GOPIO International, launched in 1989 to take up civil and human rights issues affecting overseas Indians, now claims chapters across dozens of countries.

The evening also did what such galas exist to do: it raised money and gave it away. GOPIO-CT presented $25,000 each to two local charities — Future 5 and the Children's Learning Center of Fairfield County — neither of them Indian-American organizations. That detail matters. A diaspora group writing checks to mainstream local nonprofits is making a quiet argument about belonging that no speech can match.

## Why Twenty Years Counts

For Indian-Americans, the institution-building stage of immigration is often the hardest to sustain. The first generation arrives focused on careers and children; the cultural associations they found can struggle to outlive their founders' energy. The chapters that endure tend to be the ones that broaden their mission — from organizing Diwali dinners to weighing in on local policy, youth mentorship, and public health.

GOPIO-CT's trajectory follows exactly that arc. With Connecticut's South Asian population still growing, the chapter described its work as having shifted "from cultural preservation to active participation in public policy, economic development, and community health initiatives." India's Deputy Consul General in New York, Vishal Harsh, the evening's chief guest, called the American diaspora "a global benchmark."

Benchmarks, though, are set by people who keep showing up. Two decades in, a banquet hall in Darien was less a victory lap than evidence of a community that has learned how to last."""

article2_body = """The Association of Indians in America's New York chapter is older than most of the people it now honors. Founded in 1967, AIA-NY bills itself as the oldest national association of Asian Indians in the country — which means its annual gala is one of the few diaspora events that can claim to have watched the entire arc of post-1965 Indian migration to America unfold.

This year's edition, held before more than 300 guests at Terrace on the Park in Flushing, leaned into that longevity. The chapter honored seven people it called "Ratnas," or jewels, and the list was a deliberate cross-section of where Indian-Americans have planted themselves: medicine, law, research, entrepreneurship, and technology.

## The Honorees

The senior figure of the evening was Dr. Dattatreyudu Nori, an oncologist who has spent more than five decades advancing cancer care at institutions including Memorial Sloan Kettering and Cornell Medical Center. He has authored over 300 scientific papers and holds the Ellis Island Medal of Honor along with the Padma Shri and, this year, the Padma Bhushan — India's third-highest civilian award.

Alongside him, the chapter recognized a generation still mid-career. Dr. Sahil Khera of Mount Sinai Heart, who has performed more than 2,000 structural heart procedures, was honored for his work in minimally invasive valve therapies. Dr. Aprajita Mattoo of NYU Langone, a transplant nephrologist, was cited for her role in the historic pig-to-human kidney transplant trials — work at the frontier of solving the organ-shortage crisis. Dr. Jagat Rawal, a Queens physician of more than three decades who kept his office open through the pandemic, was recognized for community medicine.

The list extended beyond medicine. Manish Dhadda, co-founder of the jewelry firm VIBHOR, was honored as an entrepreneur and philanthropist. Jessica Kalra, an attorney who once worked in the office of Senator Hillary Clinton, took the recognition in law. And the youngest honoree, Pulkita Kini — a Harvard MBA student building an AI startup after stints at Microsoft and Cloudflare — represented the generation that will define the diaspora's next chapter.

## A Gala as a Census

It is tempting to dismiss community galas as self-congratulation in rented ballrooms. But read carefully, an honoree list is a kind of census. AIA-NY's seven jewels track the professional concentrations that have defined Indian-American success — heavy in medicine, increasingly in technology and finance — while quietly registering a generational handoff.

The presence of dignitaries underlined the community's political weight. New York State Comptroller Thomas DiNapoli spoke at the event; messages came from State Senator John Liu, Nassau County Executive Bruce Blakeman, Suffolk County Executive Edward Romaine, and the Consulate General of India. Elected officials do not turn out for communities they can ignore at the ballot box.

## Belonging on the Calendar

AIA-NY also used the gala to announce its 39th Deepavali Celebration and Live Fireworks, scheduled for October 3 at Overlook Beach on Long Island. The detail is easy to skip past, but a Diwali fireworks display entering its fourth decade is its own quiet milestone. It means the festival has outlived the novelty phase that greets most immigrant traditions and settled into the fixed rhythm of a region's civic calendar.

That, ultimately, is what the oldest Indian-American association in the country is selling: not arrival, which it documented long ago, but permanence. The honorees change each year. The institution does not.

For a diaspora whose story is often told through individual breakthroughs — the first Indian-American this, the youngest that — an organization quietly entering its sixth decade offers a different and more durable kind of proof. Communities are not built by exceptional individuals alone. They are built by the people who keep the lights on between galas, year after unremarkable year, until one day the tradition is simply assumed."""

article3_body = """For the global Indian diaspora, the most consequential election of 2025 was not held in any of its usual capitals of attention — not Washington, not London, not Ottawa. It was held on an island of 1.4 million people off the coast of Venezuela, and its winner is a 73-year-old lawyer whose great-grandparents arrived as indentured laborers from India.

Kamla Persad-Bissessar was sworn in for a second, non-consecutive term as prime minister of Trinidad and Tobago on May 1, after her United National Congress won 26 of 41 parliamentary seats in the April 28 general election. The diaspora's community organizations have only recently begun to register what the result means, and the Global Organization of People of Indian Origin (GOPIO) issued a formal welcome this week, calling her a long-standing friend it first hosted in 1999.

## The Longest Diaspora

Most stories about the Indian diaspora are stories of recent arrival — the engineer who landed in the 1990s, the student who came for a master's degree. Trinidad's Indian community is something else entirely. Beginning in 1845, the British shipped indentured laborers from India to work the sugar estates of the Caribbean after the abolition of slavery. Their descendants now make up the largest ethnic group in Trinidad and Tobago, and they have spent generations negotiating a question the newer diaspora is only beginning to face: what does Indian identity mean after the connection to India itself has thinned across a century and a half?

Persad-Bissessar embodies that long arc. She is descended from indentured immigrants, was educated partly in the region and partly abroad, and rose through Trinidadian politics to become, in 2010, the country's first female prime minister. She was also the first woman of Indian origin to lead any nation outside India and the subcontinent — a distinction that places her in a small, scattered company that includes the late Cheddi Jagan of neighboring Guyana.

## Why It Resonates Beyond the Caribbean

The diaspora's interest in Persad-Bissessar is not merely sentimental. Her return matters because it complicates the dominant narrative of Indian success abroad, which tends to fixate on Silicon Valley boardrooms and Ivy League faculties. The Caribbean diaspora is older, more working-class in its origins, and culturally distinct — its Hindi survives mostly in religious ritual and chutney music rather than in daily speech.

GOPIO, which has hosted Persad-Bissessar at conventions in New York, Port of Spain, and Kolkata over the years, framed her election as an opportunity to strengthen its chapters across the Caribbean, "where the diaspora people of Indian origin have deep roots." The organization's chairman, Dr. Thomas Abraham, recalled that her late mentor, former prime minister Basdeo Panday, had long championed regional Indian identity.

## The Politics of a Returning Leader

Persad-Bissessar's victory ended a decade of People's National Movement rule and was, by the account of her own party organizers, the UNC's best result since its founding. International recognition followed quickly: U.S. Secretary of State Marco Rubio called to congratulate her within days, citing "deep historic ties" and regional security cooperation. CARICOM and neighboring Caribbean leaders sent their own statements.

Her challenges are familiar to anyone who follows small open economies — violent crime, energy revenues, and the management of an oil-and-gas sector under pressure. But for the diaspora, the symbolism runs deeper than policy. Here is a descendant of indentured laborers, twice entrusted with running her country, governing a nation where Indian-origin citizens are not a striving minority but a foundational community.

It is a useful corrective. The Indian diaspora did not begin with the H-1B visa, and its definition of success was never confined to corporate titles. Sometimes it looks like a great-granddaughter of estate workers, taking the oath of office for the second time, in a country her ancestors reached in the hold of a ship."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "A Connecticut Diaspora Chapter Turned 20. Its Guest List Was a Map of How Far Indian-Americans Have Come.",
        "subheadline": "GOPIO-CT honored a state senator, a bank CEO, and three others at its 20th anniversary gala — and gave away $50,000 to two non-Indian local charities in the process.",
        "slug": make_slug("gopio-ct-20th-anniversary-banquet-indian-american-leaders-connecticut"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "For Indian-Americans, founding a cultural association is easy; keeping one alive for two decades is the hard part. GOPIO-CT's milestone shows what it takes for an immigrant community organization to outlive its founders and graduate from Diwali dinners to public policy, youth charity, and a recognized voice in state affairs.",
        "tags": ["nri", "diaspora", "gopio", "connecticut", "indian-american", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — GOPIO-CT Marks 20th Anniversary", "url": "https://theindianeye.com/2026/06/19/gopio-ct-marks-20th-anniversary-honors-distinguished-leaders/"},
            {"name": "The Indian Eye — GOPIO-CT To Honor Five Indian American Achievers", "url": "https://theindianeye.com/2026/05/29/gopio-ct-to-honor-five-indian-american-achievers-at-its-20th-anniversary/"}
        ]),
        "score_total": 74,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/6412253/pexels-photo-6412253.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Hands raise a trophy skyward, evoking the awards presented at a community recognition gala",
        "image_attribution": "Pexels",
        "body": article1_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "America's Oldest Indian Association Honored Seven 'Jewels.' The List Doubled as a Census of the Diaspora.",
        "subheadline": "Founded in 1967, AIA-NY has watched the entire arc of Indian migration to America. Its 2026 gala honored oncologists, a transplant pioneer, and a Harvard MBA building an AI startup.",
        "slug": make_slug("aia-ny-benefit-gala-2026-ratnas-indian-american-honorees-new-york"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "An honoree list is a quiet census. AIA-NY's seven 'Ratnas' track exactly where Indian-Americans have concentrated — heavy in medicine, rising in tech and finance — while documenting a generational handoff from five-decade veterans to a 20-something founder. It also shows the value of an institution that has outlasted six decades of arrivals.",
        "tags": ["nri", "diaspora", "aia-ny", "new-york", "indian-american", "community"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — AIA-NY Hosts Grand Annual Benefit Gala 2026", "url": "https://theindianeye.com/2026/06/11/aia-ny-hosts-grand-annual-benefit-gala-2026-to-honor-individuals-for-outstanding-contributions/"},
            {"name": "Association of Indians in America — New York Chapter", "url": "https://www.aianyorg.com/"}
        ]),
        "score_total": 72,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/36121661/pexels-photo-36121661.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A Bharatanatyam dancer performs in traditional attire, of the kind featured at Indian-American community galas",
        "image_attribution": "Pexels",
        "body": article2_body
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The Diaspora's Most Remarkable 2025 Election Win Came From an Island of 1.4 Million — and a Great-Granddaughter of Indentured Laborers",
        "subheadline": "Kamla Persad-Bissessar, sworn in for a second term as Trinidad and Tobago's prime minister, complicates the Silicon-Valley story of Indian success abroad with a far older one.",
        "slug": make_slug("kamla-persad-bissessar-trinidad-prime-minister-caribbean-indian-diaspora"),
        "category": "nri-world",
        "vertical": "nri-world",
        "diaspora_angle": "The dominant narrative of the Indian diaspora fixates on recent, professional, US-and-UK arrivals. Trinidad's 180-year-old Indian community — descendants of indentured estate laborers — is the diaspora's longest experiment in what Indian identity becomes after a century and a half away from India. Persad-Bissessar's return puts that story back at the center.",
        "tags": ["nri", "diaspora", "trinidad", "caribbean", "indo-caribbean", "politics", "gopio"],
        "urgency": "medium",
        "sources": json.dumps([
            {"name": "The Indian Eye — GOPIO Welcomes Election of Kamla Persad-Bissessar", "url": "https://theindianeye.com/2026/06/18/gopio-international-welcomes-the-election-of-kamla-persad-bissessar/"},
            {"name": "Wikipedia — Kamla Persad-Bissessar", "url": "https://en.wikipedia.org/wiki/Kamla_Persad-Bissessar"},
            {"name": "U.S. Department of State — Secretary Rubio's Call with PM Persad-Bissessar", "url": "https://www.state.gov/secretary-rubios-call-with-prime-minister-persad-bissessar-of-trinidad-and-tobago/"}
        ]),
        "score_total": 76,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/06/Kamla_Persad_Bissessar.jpg",
        "image_caption": "Kamla Persad-Bissessar, prime minister of Trinidad and Tobago and a descendant of Indian indentured laborers",
        "image_attribution": "Wikimedia Commons",
        "body": article3_body
    }
]

for art in articles:
    wc = len(art["body"].split())
    print(f"[{art['slug']}] word count: {wc}")
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
