#!/usr/bin/env python3
"""NRI World Writer — 2026-06-11 18:00 UTC run. Three articles."""

import json, os, uuid, re, requests, io
from datetime import datetime, timezone
from pathlib import Path

# --- Supabase env ---
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
    if r.status_code >= 400:
        print(f"  ERROR {r.status_code}: {r.text[:300]}")
    r.raise_for_status()
    return r.json()

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")

# --- Image helpers ---
try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

def compress_image(img_bytes, max_width=1200, quality=80):
    if not HAS_PIL:
        return img_bytes
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def upload_to_supabase(img_url, filename):
    """Download, compress, upload to Supabase article-images bucket."""
    try:
        r = requests.get(img_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=20)
        r.raise_for_status()
        compressed = compress_image(r.content)
        if len(compressed) < 5000:
            print(f"  ⚠ Image too small ({len(compressed)} bytes), using original URL")
            return img_url
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(upload_url, headers={
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": "image/jpeg",
            "x-upsert": "true",
        }, data=compressed, timeout=30)
        if resp.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✅ Uploaded to Supabase: {filename} ({len(compressed)} bytes)")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({resp.status_code}): {resp.text[:100]}")
            return img_url
    except Exception as e:
        print(f"  ⚠ Image upload error: {e}")
        return img_url


# ================================================================
# ARTICLE 1: TANA Community Events Surge Across America
# ================================================================

art1_id = str(uuid.uuid4())
art1_slug = make_slug("tana-telugu-community-events-kalyanam-pickleball")

art1_body = """The Telugu Association of North America is having a moment. In the space of a single week this June, the diaspora organisation staged a grand Hindu wedding ceremony in suburban New York and a pickleball tournament that drew more than sixty-five teams to a small city in North Carolina — two events that, taken together, capture the widening ambition of America's Telugu community infrastructure.

On 6 June, TANA's New York chapter organised Sri Srinivasa Kalyanam at a Hindu temple in Hicksville, Long Island. The celestial wedding — a dramatic re-enactment of Lord Venkateswara's marriage to Goddess Padmavathi — was conducted with full Tirumala Tirupati Devasthanams rituals, complete with Vedic priests, elaborate floral mandapam decorations, and the distribution of Tirupati laddu prasadam to hundreds of attendees. For many first-generation immigrants in the New York metropolitan area, the event offered something that a weekend puja at home cannot: the sensory and spiritual scale of a Tirupati pilgrimage, transplanted to the American suburbs.

## Pickleball, Telugu-Style

A day or two later and six hundred miles south, TANA's sports wing hosted its Summer Games Pickleball Tournament in Kannapolis, North Carolina — a small city northeast of Charlotte that has become an unlikely hub for Telugu community gatherings. Sixty-five teams competed across multiple skill brackets, making it one of the largest diaspora-organised pickleball events in the southeastern United States.

The tournament is part of TANA's broader push into competitive recreational sports, a category the organisation has historically ceded to cricket leagues and badminton clubs. Pickleball's accessibility — lower barrier to entry than tennis, playable across age groups, and explosively popular in American suburbs where Telugu families have clustered — has made it a natural vehicle for community-building.

"We had families driving in from Atlanta, Raleigh, even Tampa," said a TANA volunteer involved in the event's logistics. "The sports events bring out people who wouldn't necessarily come to a cultural programme."

## Building Beyond the Temple

The pairing of a sacred ceremony and a sports tournament in a single week is not accidental. TANA, founded in 1977, has spent nearly five decades as the institutional backbone of Telugu life in America. Its biennial conferences — massive, multi-day affairs that attract tens of thousands — remain the flagship. But the organisation has been deliberately diversifying its programming in recent years, moving beyond the conference-and-cultural-show model toward year-round engagement.

That shift reflects a demographic reality. The Telugu diaspora in the United States has grown rapidly since the late 1990s, driven by the technology boom that drew tens of thousands of professionals from Andhra Pradesh and Telangana to American tech corridors. Today, Telugu is among the fastest-growing Indian languages in the U.S., and the community's geographic footprint has expanded far beyond the original clusters in New Jersey, the San Francisco Bay Area, and the Dallas–Fort Worth metroplex.

As the community has grown, so has the demand for programming that serves second-generation families, retirees who have joined their children in the U.S., and young professionals who may feel only loosely connected to the temple circuit. TANA's regional chapters — there are now more than forty across North America — have responded by adding health camps, career workshops, youth leadership summits, and sporting events to their calendars.

## The NRI Organisational Playbook

TANA is not alone in this expansion. The American Telugu Association, the Telugu Association of Greater Chicago, and dozens of city-level Telugu organisations are all investing in similar programming. But TANA's scale — its membership runs into the tens of thousands, and its treasury is among the largest of any Indian diaspora body in the U.S. — gives it an outsized capacity to set the template.

The Hicksville Kalyanam and the Kannapolis pickleball tournament, modest events in isolation, are data points in a larger pattern: the Telugu diaspora in America is building an institutional layer that goes well beyond nostalgia. It is creating infrastructure — spiritual, recreational, social — designed to keep a far-flung community cohesive across generations and geographies."""

print("--- Article 1: TANA Community Events ---")
art1_raw_img = "https://images.pexels.com/photos/16233914/pexels-photo-16233914.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_img = upload_to_supabase(art1_raw_img, f"{art1_id}.jpg")

art1 = {
    "id": art1_id,
    "headline": "From Temple Weddings to Pickleball Courts: TANA Is Rewriting the Telugu Diaspora Playbook",
    "subheadline": "A grand Kalyanam in New York and a 65-team pickleball tournament in North Carolina show how America's Telugu community is building year-round institutional infrastructure.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "TANA's expansion from biennial conferences to year-round events — spiritual, recreational, professional — mirrors the Telugu diaspora's growth into one of America's fastest-expanding Indian language communities.",
    "tags": ["nri", "diaspora", "telugu", "tana", "community", "pickleball", "kalyanam", "cultural-events"],
    "urgency": "medium",
    "sources": json.dumps(["todaytelugu.net", "NRI Connect My India", "TANA Official"]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img,
    "image_caption": "Indian community cultural celebrations — TANA is expanding its programming from conferences to year-round events across America",
    "image_attribution": "Pexels / Teja J",
    "body": art1_body.strip(),
}

try:
    sb_post("p2_articles", art1)
    print(f"✅ {art1['slug']}")
except Exception as e:
    print(f"❌ {art1['slug']}: {e}")


# ================================================================
# ARTICLE 2: Indian American Lawmakers Lead State-Level ICE Reform
# ================================================================

art2_id = str(uuid.uuid4())
art2_slug = make_slug("indian-american-lawmakers-state-legislature-ice-reform")

art2_body = """Two Indian American state legislators in the northeastern United States have emerged as leading voices in a growing movement to limit the reach of federal immigration enforcement within state borders — a development that places members of the diaspora at the centre of one of America's most contentious political debates.

In Pennsylvania, State Senator Nikil Saval, a Democrat representing Philadelphia, has become a prominent figure in what advocates call the "ICE Out" legislative initiative. The effort seeks to restrict state and local cooperation with U.S. Immigration and Customs Enforcement, particularly in contexts where state-funded institutions — schools, hospitals, courts — might be pressed into serving as de facto enforcement checkpoints.

In neighbouring New Jersey, Assemblyman Ravinder Bhalla, a Democrat from Hoboken and the city's former mayor, has co-sponsored what its authors have titled the Fight Unlawful Conduct and Keep Individuals and Communities Empowered Act. The legislation, introduced in June 2026, would limit ICE's ability to conduct enforcement operations in or near state-regulated facilities without a judicial warrant.

## Two Paths, One Community

Saval and Bhalla arrived at state politics through very different routes. Saval, the son of Indian immigrants, is a former literary editor who co-founded the tenants'-rights organisation Philadelphia Reclaim before winning his Senate seat in 2020. His politics are progressive and explicitly movement-driven; he has championed rent control, public transit funding, and workers' rights alongside immigration protections.

Bhalla, a Sikh American attorney, became Hoboken's first turbaned Sikh mayor in 2017 after a campaign that was itself shadowed by hate — flyers depicting him with the caption "Don't let TERRORISM take over our town" were distributed in the final days before the election. He won anyway, and has since built a reputation as a pragmatic executive who frames immigrant protections as a matter of local governance and public safety rather than partisan ideology.

What they share is a willingness to use state-level office to push back against what they describe as federal overreach — and, in doing so, they have placed Indian Americans in a position of legislative influence on immigration policy that would have been difficult to imagine a generation ago.

## The State-Level Battleground

The initiatives in Pennsylvania and New Jersey are part of a broader national pattern. Since the federal government intensified interior immigration enforcement in early 2025, at least fourteen state legislatures have introduced bills to define the boundaries of state cooperation with ICE. California, Illinois, and New York have enacted sanctuary-style protections; Republican-controlled states like Texas and Florida have moved in the opposite direction, requiring local law enforcement to honour ICE detainer requests.

The northeastern corridor — with its large immigrant populations, Democratic legislative majorities, and dense urban centres where federal raids carry outsized political risk — has become a particularly active front. Saval and Bhalla are not the only legislators pushing these bills, but their visibility as Indian Americans in the debate has drawn attention from diaspora media and community organisations.

## Diaspora Politics, American-Made

For the Indian American community, the emergence of Saval and Bhalla as figures in the immigration debate is significant for reasons that extend beyond the specific legislation. Indian Americans have historically been more visible in federal politics — Kamala Harris's vice presidency, Vivek Ramaswamy's presidential campaign, the growing cohort of Indian American members of Congress — than in state legislatures, where much of the policy that directly affects immigrant communities is actually made.

That is changing. The number of Indian Americans serving in state legislatures across the country has roughly doubled since 2018, driven in part by a wave of younger, community-rooted candidates who see state government as the most direct path to policy impact. Saval and Bhalla are at the leading edge of that wave.

Their work on immigration enforcement reform also complicates the popular narrative that Indian Americans, as a largely high-skilled, documented-immigration community, are detached from the broader immigrant-rights movement. Both legislators have framed their positions in universal terms: the principle that state institutions should not serve as instruments of federal enforcement, regardless of the immigration status of the individuals involved.

Whether the legislation passes in its current form is an open question. In Pennsylvania, the bill faces a divided legislature and a governor who has been cautious on immigration. In New Jersey, the political environment is more favourable but the bill must compete for floor time in a crowded session. What is not in question is that Indian American elected officials are no longer spectators in the immigration debate. They are writing the bills."""

print("--- Article 2: Indian American Lawmakers ---")
art2_raw_img = "https://images.pexels.com/photos/11838861/pexels-photo-11838861.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_img = upload_to_supabase(art2_raw_img, f"{art2_id}.jpg")

art2 = {
    "id": art2_id,
    "headline": "Two Indian American Lawmakers Are at the Centre of America's State-Level Fight Over ICE",
    "subheadline": "Nikil Saval in Pennsylvania and Ravinder Bhalla in New Jersey are drafting legislation to limit federal immigration enforcement in state institutions — placing diaspora politicians at the sharp end of the debate.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Indian Americans in state legislatures have roughly doubled since 2018. Saval and Bhalla's immigration bills show the diaspora moving from federal visibility to state-level policy influence.",
    "tags": ["nri", "diaspora", "indian-american", "politics", "state-legislature", "immigration", "nikil-saval", "ravinder-bhalla"],
    "urgency": "medium",
    "sources": json.dumps(["USA Today", "New Jersey Legislature", "Pennsylvania Senate"]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img,
    "image_caption": "Indian American lawmakers are increasingly shaping state-level policy on immigration enforcement",
    "image_attribution": "Pexels / Josh Hild",
    "body": art2_body.strip(),
}

try:
    sb_post("p2_articles", art2)
    print(f"✅ {art2['slug']}")
except Exception as e:
    print(f"❌ {art2['slug']}: {e}")


# ================================================================
# ARTICLE 3: GOPIO Proposes World's First Indian Diaspora Museum
# ================================================================

art3_id = str(uuid.uuid4())
art3_slug = make_slug("gopio-indian-diaspora-museum-delhi-proposal")

art3_body = """For a community that spans every continent and numbers upwards of thirty million, the Indian diaspora has no museum to call its own. The Global Organisation of People of Indian Origin wants to change that.

GOPIO, the umbrella body that has represented overseas Indians for nearly four decades, has formally proposed the creation of the world's first Indian Diaspora Museum. The plan, unveiled at a virtual launch event and now gaining momentum through diplomatic and philanthropic channels, envisions a permanent institution in New Delhi — a city GOPIO's leadership considers the natural home for a museum that would tell the story of Indian migration from the colonial-era indentured labour system to the twenty-first-century technology diaspora.

The proposal calls for four permanent galleries. The first would trace the history of Indian emigration from the earliest movements to Southeast Asia, the Caribbean, and East Africa through the indentured labour period that followed the abolition of slavery. The second would cover the post-independence waves: the professionals who went to the United Kingdom in the 1950s and 1960s, the Gulf migration that reshaped Kerala and Andhra Pradesh, and the technology-driven surge to the United States and Canada that began in the 1990s. A third gallery would focus on the cultural and economic contributions of the diaspora in their adopted countries — from Nobel laureates and Fortune 500 executives to the shopkeepers, nurses, and taxi drivers who built community infrastructure from scratch. The fourth, and perhaps most ambitious, would be a living, rotating exhibition space dedicated to contemporary diaspora life: identity, belonging, discrimination, dual citizenship, and the complicated relationship between homeland and adopted country.

## Heavyweight Backing

The initiative has attracted serious institutional support. The Hinduja Foundation, one of Britain's wealthiest Indian-origin philanthropic bodies, has pledged backing for the project. Ashok Amritraj, the Indian American Hollywood producer behind films such as "Machete Kills" and the "Jigsaw" franchise, has publicly endorsed the museum concept.

The museum committee is chaired by Vinod Daniel, an Australian museologist of Indian origin who has advised the development of major museums in Sydney, Singapore, and the Middle East. Daniel's involvement signals that GOPIO intends the institution to meet international museum standards — not a vanity project or a government-run exhibition hall, but a curated, research-backed institution with rotating programming and scholarly partnerships.

"There are Holocaust museums, African diaspora museums, Chinese emigration museums," Daniel said. "The Indian diaspora, one of the largest and most diverse migration stories in human history, has no equivalent institution. That gap is not just an oversight — it's a loss."

## Why Delhi, and Why Now

The choice of New Delhi is deliberate. India's capital is home to the Ministry of External Affairs, which administers the Pravasi Bharatiya Divas (Overseas Indian Day) programme and the OCI card system. It is also the seat of the Indian Council for Cultural Relations, which has funded diaspora cultural projects in the past. A Delhi location would position the museum within walking distance of the institutional machinery that shapes India's formal relationship with its overseas population.

The timing reflects a convergence of factors. India's diplomatic establishment has increasingly instrumentalised the diaspora — using it as a soft-power asset, a remittance engine, and a lobbying force in countries that matter to New Delhi's strategic interests. A museum that frames the diaspora's story in heroic, nation-building terms would serve that narrative.

But the proposal also responds to a grassroots demand. Diaspora communities from Fiji to Guyana to South Africa have long maintained local archives, oral-history projects, and community museums, often with minimal funding and volunteer labour. A central institution in India could serve as a repository, a digitisation hub, and a connective layer for these scattered efforts.

## The Road Ahead

The project is still in its early stages. GOPIO has not disclosed a fundraising target, a timeline for construction, or a specific site in Delhi. Land acquisition in the capital — where government permissions are labyrinthine and real estate is ferociously expensive — will be a formidable obstacle.

There is also the curatorial question: whose diaspora story gets told? The Indian migration experience is not one narrative but hundreds. The Tamil plantation workers of Sri Lanka and Malaysia have little in common with the Gujarati motel owners of the American interstate system, who in turn share few reference points with the Punjabi truckers of British Columbia. A museum that flattens these differences into a single triumphal arc would miss the point. One that embraces them would be genuinely new.

For now, GOPIO's proposal is a statement of intent. Whether it becomes a building — with galleries, archives, and schoolchildren on guided tours — depends on money, politics, and the willingness of India's government to make space, literally and figuratively, for a story that is as much about departure as it is about belonging."""

print("--- Article 3: GOPIO Diaspora Museum ---")
art3_raw_img = "https://images.pexels.com/photos/4072509/pexels-photo-4072509.jpeg?auto=compress&cs=tinysrgb&w=1200"
art3_img = upload_to_supabase(art3_raw_img, f"{art3_id}.jpg")

art3 = {
    "id": art3_id,
    "headline": "A Museum for Thirty Million People: GOPIO's Plan for the World's First Indian Diaspora Institution",
    "subheadline": "The Global Organisation of People of Indian Origin wants to build a permanent museum in New Delhi with four galleries tracing Indian migration from indenture to the tech boom. The Hinduja Foundation has pledged its support.",
    "slug": art3_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "A Delhi-based museum would be the first institution to curate the full arc of Indian emigration — from colonial indenture to the American tech diaspora — and could serve as a hub for scattered community archives worldwide.",
    "tags": ["nri", "diaspora", "gopio", "museum", "indian-heritage", "delhi", "migration-history", "hinduja-foundation"],
    "urgency": "low",
    "sources": json.dumps(["The Indian Eye", "GOPIO International", "Hinduja Foundation"]),
    "score_total": 70,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art3_img,
    "image_caption": "Indian heritage artefacts — GOPIO envisions four permanent galleries tracing the diaspora's journey from indenture to the technology age",
    "image_attribution": "Pexels / Binil Babu",
    "body": art3_body.strip(),
}

try:
    sb_post("p2_articles", art3)
    print(f"✅ {art3['slug']}")
except Exception as e:
    print(f"❌ {art3['slug']}: {e}")


print("\n=== NRI World Writer 2026-06-11 18:00 complete ===")
