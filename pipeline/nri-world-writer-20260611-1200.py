#!/usr/bin/env python3
"""NRI World Writer — 2026-06-11 12:00 UTC run. Three articles."""

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
# ARTICLE 1: Indian Seafarers Missing After US Strikes Tanker
# ================================================================

art1_id = str(uuid.uuid4())
art1_slug = make_slug("indian-seafarers-missing-us-strike-tanker-gulf-oman")

art1_body = """Three Indian sailors remain unaccounted for after the United States military struck an oil tanker in the Gulf of Oman on Wednesday, triggering a rare and pointed diplomatic protest from New Delhi against its closest strategic partner.

The Palau-flagged tanker Settebello was hit by what U.S. Central Command described as "precision munitions" fired into the vessel's engine room. The ship had been transiting the Gulf of Oman carrying Iranian oil and, according to Centcom, "repeatedly failed to comply with directions from American forces." It is the eighth vessel disabled since Washington launched its blockade of Iran-related shipping on 13 April.

Of the 24 crew members aboard, 21 Indian mariners were rescued by the Omani Navy, which responded to the Settebello's distress call. Three remain missing. The United Kingdom Maritime Trade Operations agency reported at least one casualty, though it remains unclear whether that individual is among the rescued or the missing.

## India Summons the U.S. Envoy

India's response was swift and unambiguous. The Ministry of External Affairs condemned what it called an "attack on the commercial vessel Settebello" and confirmed that the Indian embassy in Oman was coordinating with local authorities in the search-and-rescue operation.

More significantly, India summoned the U.S. deputy chief of mission — a step New Delhi reserves for serious diplomatic grievances — and lodged a "strong protest" against the strike, according to two Indian sources with direct knowledge of the matter.

"The targeting of commercial shipping and civilian infrastructure in the region must end," the ministry said in a statement.

The rebuke is notable because India and the United States have steadily deepened military and intelligence ties over the past decade, particularly through the Quad grouping. But the safety of Indian workers overseas — an issue that cuts across party lines and commands intense domestic attention — has historically overridden strategic alignment when New Delhi perceives its citizens to be in harm's way.

## The Broader Blockade

The strike fits within a broader American campaign to choke off Iranian oil revenue. Since the blockade began in April, after Iran curtailed shipping through the Strait of Hormuz, U.S. forces have disabled eight non-compliant vessels, redirected 134 ships that followed orders, and permitted 42 humanitarian-aid vessels to pass through.

The targets include so-called shadow fleet tankers — older, poorly insured ships flying flags of convenience to obscure their ownership, cargo and movements. The Settebello, partially laden and last tracked off Oman's coast on 1 June, fits the profile.

But for the Indian merchant marine, the geopolitics are secondary. India supplies a disproportionate share of the world's commercial seafarers — roughly 240,000 of the 1.9 million who crew international vessels. Many serve on vessels operating in the Persian Gulf and its surrounding waters, one of the most volatile shipping corridors on the planet.

## A Community on Edge

Arsenio Dominguez, secretary-general of the International Maritime Organisation, condemned the incident. "I strongly condemn any act from any party that endangers the lives of seafarers and the safety of international shipping," he said. "My thoughts are with the families of the three missing seafarers."

For the families of the missing men — and the tens of thousands of Indian mariners whose livelihoods depend on these routes — the incident is a reminder that geopolitical confrontation rarely respects the boundary between combatants and bystanders. The blockade may be aimed at Tehran, but the risk falls on the crews."""

print("--- Article 1: Seafarers ---")
# Image: Pexels oil tanker
art1_raw_img = "https://images.pexels.com/photos/27362253/pexels-photo-27362253.jpeg?auto=compress&cs=tinysrgb&w=1200"
art1_img = upload_to_supabase(art1_raw_img, f"{art1_id}.jpg")

art1 = {
    "id": art1_id,
    "headline": "Three Indian Seafarers Are Missing After a U.S. Military Strike on a Tanker Off Oman. India Has Summoned the American Envoy.",
    "subheadline": "New Delhi lodged a 'strong protest' after precision munitions hit the Settebello in the Gulf of Oman, leaving 21 Indian crew rescued and three unaccounted for.",
    "slug": art1_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "India supplies roughly 240,000 of the world's 1.9 million commercial seafarers. The blockade risks NRI lives in the Gulf's volatile shipping lanes.",
    "tags": ["nri", "diaspora", "seafarers", "gulf-of-oman", "india-us-relations", "maritime"],
    "urgency": "high",
    "sources": json.dumps(["Reuters", "India Ministry of External Affairs", "International Maritime Organisation"]),
    "score_total": 88,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art1_img,
    "image_caption": "An oil tanker at sea — Indian mariners crew a disproportionate share of the world's commercial fleet",
    "image_attribution": "Pexels",
    "body": art1_body.strip(),
}

try:
    sb_post("p2_articles", art1)
    print(f"✅ {art1['slug']}")
except Exception as e:
    print(f"❌ {art1['slug']}: {e}")


# ================================================================
# ARTICLE 2: RBI Lifts NRI/OCI Equity Investment Limits
# ================================================================

art2_id = str(uuid.uuid4())
art2_slug = make_slug("rbi-nri-oci-equity-investment-limit-sebi-10-percent")

art2_body = """For years, the biggest frustration for diaspora investors who wanted serious exposure to Indian equities was not the market itself but the paperwork surrounding it. The Reserve Bank of India has just dismantled one of the thickest layers.

Under a package of measures announced this week, the RBI said it will raise the ceiling on how much an individual Non-Resident Indian (NRI) or Overseas Citizen of India (OCI) can hold in a listed Indian company without registering as a Foreign Portfolio Investor with SEBI. The individual cap, already doubled from 5 per cent to 10 per cent of paid-up equity capital following Budget 2026, will go higher still. The combined holding limit for all such overseas individuals was also more than doubled earlier this year, from 10 per cent to 24 per cent. The RBI has signalled that both thresholds will be raised further, though the revised numbers have not been disclosed.

The central bank also extended the same simplified framework to all individual Persons Resident Outside India — not just NRIs and OCIs — widening the pool of eligible investors significantly.

## Why It Matters

The distinction between the "NRI route" and the FPI route might sound bureaucratic. It is. And that is precisely why it matters.

The FPI route requires formal SEBI registration, ongoing compliance filings, and a paper trail that is manageable for institutional money managers but impractical for a doctor in Dallas or an engineer in Dubai who wants to build a meaningful position in Infosys or HDFC Bank. The non-FPI route — the one now being expanded — lets overseas individuals invest through a Portfolio Investment Scheme (PIS) operated by designated banks, with far simpler onboarding.

Until this year, that simpler route was capped at 5 per cent of any company's equity per individual and 10 per cent in aggregate for all NRI and OCI investors. Those limits were fine for casual participants but constraining for wealthy individuals, family offices and anyone with conviction-driven portfolios.

The Budget 2026 reforms moved the goalposts once. The RBI's latest announcement moves them again — and, crucially, opens the field to a broader category of overseas investors who are not necessarily of Indian origin.

## Part of a Larger Push

The equity relaxation sits within a wider set of measures aimed at pulling foreign capital into India. In the same announcement, the RBI expanded the Fully Accessible Route for government securities by including all new 15-year, 30-year and 40-year bond issuances. It removed certain concentration and short-term investment restrictions for FPIs in government debt. And it introduced temporary incentives for external commercial borrowings and fresh FCNR(B) deposits, available until 30 September 2026.

The message is coherent: India wants more foreign capital in its equity and debt markets, and it is reducing the friction that has historically channelled that capital through narrow institutional pipes.

## What NRI Investors Should Watch

The headline direction is clear, but the details — specifically, what the new individual and aggregate caps will be — remain unknown. If the increase is substantial, it could transform the calculus for affluent NRIs who have parked money in real estate or fixed deposits because the equity route felt too constrained.

The extension to all PROIs is equally significant for a different reason: it tells foreign investors of non-Indian origin that India's equity market is not a members-only club. For an economy that wants to be the next China-scale destination for global portfolio capital, the signal matters as much as the numbers."""

print("\n--- Article 2: RBI Equity ---")
# Image: Wikimedia BSE building (original size, will be compressed)
art2_raw_img = "https://upload.wikimedia.org/wikipedia/commons/0/04/BSE_-_Bombay_Stock_Exchange_Building.jpg"
art2_img = upload_to_supabase(art2_raw_img, f"{art2_id}.jpg")

art2 = {
    "id": art2_id,
    "headline": "The RBI Just Made It Easier for NRIs to Own Bigger Stakes in Indian Companies. Here Is What Changed.",
    "subheadline": "Individual investment caps for NRIs and OCIs in listed Indian equities have already doubled to 10 per cent this year. The central bank says it will push them higher.",
    "slug": art2_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "NRI investors in the US, UK and Gulf can now build larger positions in Indian stocks without the regulatory burden of SEBI's FPI registration route.",
    "tags": ["nri", "rbi", "investment", "equity", "sebi", "oci", "indian-stocks"],
    "urgency": "medium",
    "sources": json.dumps(["Mint", "Outlook Business", "ainvest"]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art2_img,
    "image_caption": "The Bombay Stock Exchange building in Mumbai — India's oldest equities exchange",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body.strip(),
}

try:
    sb_post("p2_articles", art2)
    print(f"✅ {art2['slug']}")
except Exception as e:
    print(f"❌ {art2['slug']}: {e}")


# ================================================================
# ARTICLE 3: Bihar Launches Global Diaspora Portal
# ================================================================

art3_id = str(uuid.uuid4())
art3_slug = make_slug("bihar-global-diaspora-portal-overseas-biharis-development")

art3_body = """There are Biharis in Silicon Valley writing code, Biharis in the Gulf building skyscrapers, and Biharis in Britain running NHS wards. What there has not been, until this week, is a formal digital channel for any of them to tell their state government what they think it ought to do differently.

The Bihar government launched a "Global Diaspora Portal" on Tuesday, a platform that invites people of Bihari origin living anywhere in the world to propose ideas, volunteer expertise and pitch investment plans directly to the state administration. The portal was developed by the Department of Information Technology and launched by IT Minister Nitish Mishra.

"The people of Bihar living across the world wish to contribute to the development of their homeland, and the government is committed to providing them with a meaningful platform to do so," Mishra said at the launch event in Patna.

## Three Routes In

The portal is structured around three categories of participation. Under "Change Maker," users can submit policy ideas, innovation proposals and suggestions for state development. The "Volunteer" section allows individuals to offer skills and support for social and developmental initiatives. And the "Investment" category targets entrepreneurs and businesses interested in setting up industries, generating employment or expanding economic activity in Bihar.

The categories are broad by design. What distinguishes this effort from the usual government portal is the framing: the Bihar government is explicitly positioning the diaspora not as a source of remittances or emotional nostalgia, but as a strategic resource for the state's transformation.

## Following the AI Summit Playbook

The initiative is a direct outgrowth of the Bihar AI Summit 2026, where Chief Minister Samrat Chaudhary urged Biharis abroad to contribute to the development of their *janmabhoomi* (birthplace) alongside their *karmabhoomi* (place of work). Mishra described the portal as the practical mechanism for delivering on that call.

The timing is deliberate. Bihar has been one of the slower Indian states in attracting foreign direct investment and building a technology sector, despite producing some of the sharpest minds in the Indian diaspora. The Indian Institutes of Technology, which send a significant share of graduates to the United States, draw disproportionately from Bihar and its neighbouring states. The gap between where Biharis work and where Bihar itself stands in India's development rankings is a perennial source of both pride and frustration within the community.

## The Diaspora Portal Model

Bihar is not the first Indian state to attempt this. Kerala, Gujarat, Telangana and Andhra Pradesh have all launched diaspora engagement initiatives over the past decade, with varying degrees of success. Kerala's NORKA-Roots programme, which serves Malayali workers in the Gulf, remains the most established. Gujarat's Vibrant Gujarat summits have attracted significant NRI investment. Telangana has actively courted its tech diaspora in the United States.

What these precedents show is that success depends less on the portal itself and more on what sits behind it: a responsive bureaucracy, transparent processes and a genuine willingness to act on proposals rather than archive them. Mishra pledged that he would "personally monitor" submissions to ensure they are "examined seriously and translated into actionable outcomes." Whether that commitment survives the first surge of input will determine whether this is a platform or a PR exercise.

## A State's Bet on Its People

Bihar's pitch is unusually honest. It is not pretending to be Bangalore or Hyderabad. It is acknowledging that its greatest export has been people — and asking whether those people, having built careers in the world's most competitive economies, might now channel some of that energy homeward.

For the Bihari diaspora, the question is whether this time will be different. Many have heard versions of this call before. The portal's three-category design suggests the government at least understands that engagement means more than writing cheques. Whether Bihar is ready to absorb the ideas, energy and expectations of a global community accustomed to a faster pace of execution is the real test."""

print("\n--- Article 3: Bihar Portal ---")
# Image: Pexels Gandhi Setu Patna aerial
art3_raw_img = "https://images.pexels.com/photos/12058309/pexels-photo-12058309.jpeg?auto=compress&cs=tinysrgb&w=1200"
art3_img = upload_to_supabase(art3_raw_img, f"{art3_id}.jpg")

art3 = {
    "id": art3_id,
    "headline": "Bihar Wants Its Global Diaspora to Help Build the State. It Just Launched a Portal to Make That Possible.",
    "subheadline": "A new digital platform invites overseas Biharis to pitch ideas, volunteer expertise and propose investments directly to the state government.",
    "slug": art3_slug,
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Bihar produces some of India's sharpest minds for the global workforce but has struggled to channel diaspora expertise back into state development.",
    "tags": ["nri", "bihar", "diaspora", "india-development", "investment", "digital-india"],
    "urgency": "medium",
    "sources": json.dumps(["Patna Press", "Bihar Department of Information Technology"]),
    "score_total": 72,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": art3_img,
    "image_caption": "An aerial view of the Gandhi Setu bridge spanning the Ganges River in Patna, Bihar",
    "image_attribution": "Pexels",
    "body": art3_body.strip(),
}

try:
    sb_post("p2_articles", art3)
    print(f"✅ {art3['slug']}")
except Exception as e:
    print(f"❌ {art3['slug']}: {e}")


print("\n=== NRI World Writer complete ===")
