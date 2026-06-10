#!/usr/bin/env python3
"""
NRI World Writer — 2026-06-10
Writes 2 articles for The Videshi NRI World section.
"""
import json, os, uuid, re, io, requests
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

# Pexels key
pexels_env = Path.home() / "workspace/.env.pexels"
for line in pexels_env.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())
PEXELS_KEY = os.environ.get("PEXELS_API_KEY", "")

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

# ── Image helpers ──
def compress_image(img_bytes, max_width=1200, quality=80):
    from PIL import Image
    img = Image.open(io.BytesIO(img_bytes))
    if img.mode in ('RGBA', 'P'):
        img = img.convert('RGB')
    if img.width > max_width:
        ratio = max_width / img.width
        img = img.resize((max_width, int(img.height * ratio)), Image.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format='JPEG', quality=quality, optimize=True)
    return buf.getvalue()

def download_image(url):
    r = requests.get(url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=30)
    r.raise_for_status()
    return r.content

def upload_to_supabase(img_bytes, filename):
    upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(upload_url, headers=upload_headers, data=img_bytes, timeout=30)
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def source_and_upload_image(source_url, slug):
    """Download, compress, and upload image. Returns Supabase public URL."""
    raw = download_image(source_url)
    compressed = compress_image(raw)
    size_kb = len(compressed) / 1024
    print(f"  Image compressed: {size_kb:.0f} KB")
    filename = f"{slug}.jpg"
    public_url = upload_to_supabase(compressed, filename)
    print(f"  Uploaded: {public_url[:80]}...")
    return public_url


# ═══════════════════════════════════════════════════
# ARTICLE 1: NCAIA 20th Anniversary Gala
# ═══════════════════════════════════════════════════

art1_id = str(uuid.uuid4())
art1_slug = make_slug("ncaia-twentieth-anniversary-jesse-singh-lifetime-award-maryland")

art1_body = """The National Council of Asian Indian Associations turned twenty on a warm Friday evening in Hanover, Maryland, and its president used the occasion to remind the room that an organisation born in a conversation is only as durable as the community that keeps talking.

"Tonight is more than a celebration of an organisation," NCAIA President Anjana Bordoloi told several hundred attendees at the Clarion Hotel on June 6. "It is a celebration of vision, a journey, and a community that has flourished through dedication, service, and unity over the past two decades."

## Two decades, one mandate

NCAIA was conceived during an Indian Independence Day celebration in the Washington metropolitan area in August 2005, when a cluster of community leaders concluded that Indian Americans lacked a national platform that could speak across regional, linguistic, and generational lines. The council was formally established the following year with a mandate to promote cultural heritage, civic participation, and leadership development.

Twenty years later, the landscape it operates in has changed dramatically. The Indian American population has swelled past 5.2 million, six members of the community sit in the U.S. House of Representatives, and the diaspora's economic footprint now registers in congressional hearings and White House briefings. NCAIA founder Nagender Madhavaram, who reflected on the organisation's origins at the gala, framed the milestone in deliberately modest terms: "Twenty years is not just a number. It is a journey."

## Jesse Singh and the politics of pride without ego

The evening's centrepiece was a Lifetime Achievement Award for Jesse Singh, the founder and chairman of Sikhs of America, presented by Maryland Comptroller Brooke Lierman. Singh has spent years building his organisation's presence on Capitol Hill, championing religious freedom legislation, and working to amplify Sikh American voices in a political environment that often flattens South Asian identity into a single, undifferentiated category.

His acceptance remarks were characteristically direct — and pointedly timed. "One of the things that I'm seeing nowadays is there's a little backlash on South Asian communities," Singh told the audience, choosing the word "backlash" carefully. His prescription was not combativeness but composure: "We have to overcome by uniting and not by becoming aggressive."

Singh also turned the lens inward. "We should be proud, but we should not get egoistic," he said, a line that drew knowing nods. "We should be doubling our efforts to contribute more to this great nation."

## Maryland as microcosm

Comptroller Lierman, who oversees the state's finances, used the gala to deliver data that doubled as a political argument. Maryland is home to more than 420,000 Asian American and Pacific Islander residents, she noted, and the state's 14,000-plus Asian-owned businesses employ over 118,000 people. Together, those firms generate more than half of all revenue produced by minority-owned businesses in Maryland.

"That is not a footnote, friends, that is a foundation," Lierman said. Her broader point — that diversity is not decorative but structural — landed with particular force in a room full of professionals who have spent two decades building exactly the kind of civic infrastructure she was describing.

The evening also brought a Governor's Citation for Bordoloi, presented by Gurpreet Takhar, chair of the Governor's Commission on South Asian American Affairs, along with citations from U.S. Senator Chris Van Hollen and Montgomery County Councillor Laurie-Anne Sayles.

## The embassy takes note

Representing India's embassy in Washington, Second Secretary Rajiv Ahuja conveyed greetings from Ambassador Vinay Kwatra and described diaspora members as the "living link" and "anchor" of the India-U.S. bilateral relationship. The United States is now home to the largest Indian diaspora in the world — a fact that has transformed what was once a sentimental connection into a geopolitical asset worth tending on both sides.

The gala closed with cultural performances by local groups and a cake-cutting ceremony that felt, to those who had been in the room since 2006, like an earned exhale. NCAIA's next two decades will unfold in a country where Indian Americans are more visible, more scrutinised, and more politically consequential than at any point in the community's history. Whether that visibility translates into the kind of durable institutional power the organisation was built to cultivate is the question Madhavaram, Bordoloi, and Singh are still working to answer."""

print("📝 Article 1: NCAIA 20th Anniversary")
print("  Sourcing image...")
# Using Pexels: diverse crowd gathered at community event
pexels_url = "https://images.pexels.com/photos/16100484/pexels-photo-16100484.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_image = source_and_upload_image(pexels_url, art1_slug)

art1 = {
    "id": art1_id,
    "headline": "America's Oldest National Indian American Council Just Turned Twenty. Its Founder Wants the Next Two Decades to Be Louder.",
    "subheadline": "The NCAIA celebrated two decades of community building in Maryland with a Lifetime Achievement Award for Jesse Singh and a pointed message about navigating backlash without losing composure.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NCAIA is one of the few national organisations explicitly built to unite the diverse Indian American community across regional and generational lines — its 20th anniversary gala in Maryland spotlighted how far community infrastructure has come and how much further it needs to go.",
    "tags": ["nri", "diaspora", "indian-american", "community", "ncaia", "maryland", "civic-engagement"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "South Asian Herald", "url": "https://southasianherald.com/ncaia-celebrates-20th-anniversary-honors-jesse-singh-with-lifetime-achievement-award/"},
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/preview/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"}
    ]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_image,
    "image_caption": "Indian community members gathering at a cultural celebration",
    "image_attribution": "Pexels",
    "body": art1_body,
}


# ═══════════════════════════════════════════════════
# ARTICLE 2: Carnegie IAAS 2026 — Discrimination & Self-Censorship
# ═══════════════════════════════════════════════════

art2_id = str(uuid.uuid4())
art2_slug = make_slug("indian-americans-self-censoring-discrimination-carnegie-survey")

art2_body = """Half of all Indian Americans say they have experienced discrimination since the start of 2025. One in four has been called a slur. Nearly half encounter racist social media posts targeting their community on a regular basis.

These are not anecdotes. They are data points from the 2026 Indian American Attitudes Survey, a nationally representative study of 1,000 Indian American adults conducted by the Carnegie Endowment for International Peace in partnership with YouGov. The findings paint a picture of a community that is not merely enduring hostility but quietly reorganising its daily life to avoid it.

## The numbers behind the silence

The survey asked respondents whether they had changed their behaviour since the start of 2025 due to concerns about discrimination or racism directed at Indians or Indian Americans. The results are striking for what they reveal about the invisible costs of belonging.

Thirty-one per cent of respondents — nearly one in three — report avoiding discussing or engaging with politics on social media. Twenty-one per cent have stopped displaying political signs or bumper stickers. Nineteen per cent say they have avoided publicly wearing Indian dress or attire. Twenty-one per cent report avoiding leaving and re-entering the United States altogether, a staggering concession for a community with deep transnational ties. Eighteen per cent have stayed away from political rallies or protests.

These are not the responses of a community in crisis. They are the responses of a community performing a daily calculus of visibility — deciding, meal by meal and outfit by outfit, how Indian to appear in public.

## Where the hostility lives

The survey's data on where discrimination occurs is equally revealing. Among those who reported personal experiences, the most common settings were stores or malls (42 per cent) and job applications (38 per cent). Thirty-one per cent reported incidents while participating in cultural or religious activities — a category that encompasses everything from temple visits to Diwali celebrations to weekend language classes.

Online, the numbers are worse. Forty-eight per cent of respondents encounter racist posts targeting Indians or Indian Americans "very or somewhat often." When shown an example of such a post, half reported feeling angry, a third felt anxious, and nearly a third felt fearful.

The Carnegie study is the third wave of the IAAS, following earlier surveys in 2020 and 2024. One of its most counterintuitive findings is that the share of respondents reporting direct personal discrimination — roughly 50 per cent — has remained remarkably stable across all three waves. The researchers suggest a disquieting explanation: the stability may reflect not a plateau in hostility, but an increase in avoidance behaviour that keeps reported rates from climbing further.

## The community fights back — with paperwork

If the Carnegie data captures the problem, the Indian American Advocacy Council's response illustrates how community organisations are scrambling to address it. The IAAC has published a 10-page "Know Your Rights" guide designed for Indian Americans across visa statuses — H-1B holders, F-1 students, H-4 dependents, green card holders, and citizens.

The guide is notably practical. It outlines what to do during encounters with ICE agents, explains workplace protections under the Civil Rights Act of 1964, provides step-by-step instructions for documenting hate incidents (date, time, location, photographs, witness statements), and lists reporting channels from the Department of Justice Civil Rights Division to the FBI.

The IAAC reports that online slurs targeting Indians increased by 115 per cent between 2023 and 2025. It has identified Frisco, Texas — a fast-growing suburb in the Dallas-Fort Worth metroplex with a rapidly expanding Indian American population — as a particular "flashpoint," where local government meetings have drawn outside activists spreading claims of an "Indian takeover."

## Political flux and the party problem

The discrimination data lands in a political environment where Indian Americans' traditional allegiances are under strain. The Carnegie survey finds that 71 per cent disapprove of Trump's second-term performance, but the community's attachment to the Democratic Party has weakened. Republican identification has increased modestly since 2020, and the share of self-identified moderates — the largest ideological group — suggests a community less interested in partisan loyalty than in pragmatic calculation.

The 2024 election saw Trump make notable gains among Indian American men in particular, narrowing the Democratic margin from roughly 70–20 to about 60–30. In 2026, support for Trump has softened, but Democratic support has not rebounded commensurately. The result is a growing cohort of Indian Americans who disapprove of both major parties — disaffected moderates who vote but feel unrepresented, and who are increasingly likely to make their electoral choices on immigration and economic policy rather than identity.

## The 40 per cent question

Perhaps the most telling number in the entire survey: when asked whether they had ever thought about leaving the United States, 40 per cent said yes — frequently, occasionally, or rarely. Among those who had considered it, the most cited reason was frustration with U.S. politics (58 per cent), followed by cost of living (54 per cent) and personal safety (41 per cent).

But here is the twist: most of those who have thought about leaving do not plan to return to India. Only one in four cited India as their potential destination. Sixty-two per cent named some other country. The community is not fantasising about going home. It is fantasising about going somewhere else — a distinction that says more about the current American moment than any policy brief could."""

print("\n📝 Article 2: Carnegie IAAS — Discrimination & Self-Censorship")
print("  Sourcing image...")
# Using Pexels: diverse group with Indian flag
pexels_url2 = "https://images.pexels.com/photos/8770960/pexels-photo-8770960.jpeg?auto=compress&cs=tinysrgb&w=1200"
art2_image = source_and_upload_image(pexels_url2, art2_slug)

art2 = {
    "id": art2_id,
    "headline": "One in Four Indian Americans Has Been Called a Slur Since January. A Landmark Survey Maps What Happens Next.",
    "subheadline": "Carnegie's 2026 Indian American Attitudes Survey reveals a community that isn't just enduring hostility — it's quietly reorganising daily life to avoid it. Nearly a third have stopped discussing politics online. One in five has stopped wearing Indian dress in public.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The survey captures something rarely quantified about diaspora life: the daily calculus of visibility, where Indian Americans decide how visibly Indian to be in public spaces as discrimination concerns reshape civic participation, dress, travel, and political expression.",
    "tags": ["nri", "diaspora", "discrimination", "indian-american", "carnegie", "survey", "self-censorship", "hate-crimes"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/preview/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "IAAC Know Your Rights Guide (GG2)", "url": "https://www.gg2.net/iaac-know-your-rights-guide-us-concerns/"},
        {"name": "Indian American Impact Summit", "url": "https://theindianeye.com"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_image,
    "image_caption": "Indian Americans celebrating cultural identity at a community gathering",
    "image_attribution": "Pexels",
    "body": art2_body,
}


# ── Insert articles ──
print("\n🚀 Inserting articles into Supabase...")
for art in [art1, art2]:
    try:
        sb_post("p2_articles", art)
        print(f"  ✅ {art['slug']}")
    except Exception as e:
        print(f"  ❌ {art['slug']}: {e}")

print("\n✅ NRI World writer complete.")
