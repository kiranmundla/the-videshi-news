#!/usr/bin/env python3
"""Immigration writer — June 4, 2026, 4:00 PM UTC run"""
import json, os, uuid, re, io, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env files
for env_file in [Path.home() / ".env.supabase", Path.home() / "workspace" / ".env.pexels"]:
    if env_file.exists():
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
UA = {"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

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

def upload_to_supabase(img_bytes, filename):
    """Upload compressed image to Supabase article-images bucket."""
    compressed = compress_image(img_bytes)
    print(f"  Compressed: {len(img_bytes)} → {len(compressed)} bytes")
    upload_headers = {
        "apikey": SB_KEY,
        "Authorization": f"Bearer {SB_KEY}",
        "Content-Type": "image/jpeg",
        "x-upsert": "true",
    }
    r = requests.post(
        f"{SB_URL}/storage/v1/object/article-images/{filename}",
        headers=upload_headers,
        data=compressed,
        timeout=30,
    )
    r.raise_for_status()
    return f"{SB_URL}/storage/v1/object/public/article-images/{filename}"

def download_image(url):
    """Download image with proper headers."""
    r = requests.get(url, headers=UA, timeout=15)
    r.raise_for_status()
    ct = r.headers.get("Content-Type", "")
    if not ct.startswith("image/"):
        raise ValueError(f"Not an image: {ct}")
    if len(r.content) < 5000:
        raise ValueError(f"Image too small: {len(r.content)} bytes")
    return r.content

now = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def make_slug(base):
    slug = base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    return slug[:70].rstrip('-') + "-" + datetime.now().strftime("%Y%m%d")


# ── ARTICLE 1: EB-5 September 30 Deadline ──────────────────────────

art1_id = str(uuid.uuid4())
art1_slug = make_slug("eb5-800k-window-closing-september-30-indian-h1b-green-card")

art1_body = """The September 30 deadline is not the kind that slides. For Indian H-1B workers eyeing the EB-5 investor visa as an escape from the employment-based green card backlog, the next 118 days represent a closing window that will not reopen on the same terms.

Under the EB-5 Reform and Integrity Act of 2022, which reauthorised the Regional Center Program, investors who file Form I-526E on or before September 30, 2026, receive statutory grandfathering protection. This means that even if Congress fails to extend the programme beyond its September 30, 2027, sunset date, petitions filed before the earlier deadline will continue to be processed. File after September 30, 2026, and that protection vanishes.

## The price is going up

The current minimum investment for a Targeted Employment Area (TEA) project — which includes high-unemployment and rural zones — stands at $800,000. The standard threshold is $1,050,000. But immigration attorneys and EB-5 operators are already flagging the next adjustment. Golden Gate Global, one of the largest regional centre operators, projects the TEA minimum will rise to between $940,000 and $950,000 in early 2027. That is a $140,000 to $150,000 increase for waiting four months too long.

"The fear that India may backlog, and we may have a retrogression, and so be unable to file a concurrent AOS, may be a stimulus for the EB-5 visa applications," Rohit Turkhud, an EB-5 attorney at CSG Law, told EB5Investors.com. "Applications filed on or before September 30, 2026, will be grandfathered despite the present RIA being in effect until September 2027, which may also be motivating folks to apply now."

## Why H-1B workers are turning to EB-5

The arithmetic is unforgiving. Indian nationals hold more than 72 per cent of all H-1B visas, according to the Department of Homeland Security. The EB-2 backlog for India stretches back to July 2014 in the current final action dates. The EB-3 queue is similarly glacial. Former State Department official Charlie Oppenheim has warned that even the recent forward movement in India's employment-based dates is "artificial" — driven by the 75-country visa processing suspension — and could boomerang sharply once restrictions lift.

Against that backdrop, the EB-5 programme offers something the employment-based categories do not: employer independence. An approved I-526E petition, combined with a concurrently filed I-485 adjustment of status application, delivers an Employment Authorisation Document (EAD) for unrestricted work within months. Add Advance Parole for international travel without visa restamping, and the practical advantages over an H-1B are considerable.

## The concurrent filing advantage — for now

The 2022 reforms introduced set-aside visa categories within EB-5: 20 per cent for rural projects, 10 per cent for high-unemployment areas, and 2 per cent for infrastructure projects. Critically, priority dates in these set-aside categories remain current for Indian nationals, meaning concurrent filing of I-526E and I-485 is available today. File both forms, and you are in authorised stay while USCIS adjudicates your green card. Your H-1B status becomes irrelevant.

But that window is narrowing. Fragomen, one of the world's largest immigration law firms, notes that Indian demand for EB-5 set-aside visas is rising rapidly. If applications from India continue to surge, cut-off dates could be imposed on reserved categories too — eliminating the concurrent filing advantage that makes the programme so attractive for H-1B holders.

## What it takes to file by September 30

The filing deadline is not a deadline to start thinking about EB-5 — it is a deadline to have a completed petition in the hands of USCIS. Source-of-funds documentation alone takes months. Investors must demonstrate the lawful origin of their capital through tax returns, company financials, bank statements, gift deeds, and remittance records. For Indian nationals, compliance with the Reserve Bank of India's Liberalised Remittance Scheme (LRS) adds another layer of documentation and transfer logistics.

Project due diligence is equally time-consuming. A properly vetted EB-5 investment requires reviewing offering documents, job-creation models, escrow structures, and the track record of the regional centre operator. CMB Regional Centers, one of the oldest in the industry, received I-956F project approval from USCIS on June 3 for its latest student housing project — a reminder that USCIS is actively processing and approving new offerings.

The message from every corner of the EB-5 industry is the same: if you are an Indian H-1B holder with the capital, the documentation runway, and the appetite for a permanent solution, the clock is already running. September 30 does not negotiate."""

# Image for Article 1: Green card from Wikimedia Commons
print("📸 Sourcing image for Article 1 (EB-5)...")
try:
    img1_bytes = download_image("https://upload.wikimedia.org/wikipedia/commons/4/49/2023_green_card_front.jpg")
    art1_img = upload_to_supabase(img1_bytes, f"{art1_id}.jpg")
    art1_caption = "A United States permanent resident card — the goal at the end of the EB-5 investor visa process"
    art1_attribution = "Wikimedia Commons"
    print(f"  ✅ Uploaded: {art1_img}")
except Exception as e:
    print(f"  ⚠ Image failed: {e}")
    art1_img = ""
    art1_caption = ""
    art1_attribution = ""


# ── ARTICLE 2: Senate Vote-a-Rama ──────────────────────────────────

art2_id = str(uuid.uuid4())
art2_slug = make_slug("senate-70b-vote-a-rama-ice-cbp-enforcement-indian-visa")

art2_body = """The Senate voted 53-46 on Wednesday to advance a roughly $70 billion budget reconciliation package funding Immigration and Customs Enforcement and Customs and Border Protection — the most significant single allocation for immigration enforcement since the Department of Homeland Security was created in 2003. On Thursday, the chamber begins its vote-a-rama, a marathon of amendments that could reshape the bill's final form before passage.

For the estimated 600,000 Indian nationals on H-1B visas, the bill's passage is not an abstraction. It is the funding mechanism for the enforcement apparatus that already touches their daily lives — from FDNS site visits at their offices to the social media vetting that has delayed consular appointments by months.

## What is in the $70 billion

The reconciliation package, designated S. 2, allocates $38.5 billion to ICE and $26 billion to Customs and Border Protection. All funds remain available through fiscal year 2029, giving the enforcement agencies a four-year war chest that outlasts the current administration.

Bloomberg Law's analysis of updated Senate Judiciary Committee text, released on June 3, notes that the committee dropped a controversial $1 billion provision from the package. The remaining funds are overwhelmingly directed at interior enforcement and border operations — precisely the functions that affect legal visa holders through compliance checks, workplace investigations, and deportation proceedings.

## The settlement fund that will not die

The bill's most politically volatile provision has nothing to do with visas. A proposed $1.776 billion fund — intended to compensate individuals whom the Trump administration claims were victims of government "weaponisation" — nearly derailed the legislation before it reached the floor.

Acting Attorney General Todd Blanche told House lawmakers on Tuesday that "we are not moving forward with the fund, period." Hours later, Trump contradicted him at the White House, telling reporters: "I love it. I think it's so important." When asked whether the fund was dead or merely paused, the president answered: "I'd have to ask the lawyers, I don't know."

Senate Democrats and some Republicans plan to force votes during Thursday's amendment session to permanently ban the settlement fund. Senator Thom Tillis, a North Carolina Republican, has said he will offer his own amendment to block any resurrection. Senate Majority Leader John Thune acknowledged the controversy but kept his focus narrow: "Right now, the goal is to get the base bill across the finish line."

## Why Indian visa holders should watch the amendments

The vote-a-rama is Congress's procedural free-for-all — any senator can offer amendments, and votes happen in rapid succession with minimal debate. While most amendments are messaging exercises designed to force politically uncomfortable votes, some can alter the bill's substance.

For Indian visa holders, the amendments to watch are those touching interior enforcement funding, USCIS fee structures, and any provisions that could affect the processing of work visa extensions or adjustment-of-status applications. The reconciliation bill already codifies several provisions of the One Big Beautiful Bill Act, including the new $250 I-94 fee and tightened EAD validity periods. Additional amendments could expand or restrict these measures.

The ICE funding is particularly consequential. The Fraud Detection and National Security Directorate (FDNS), which conducts unannounced site visits to H-1B workplaces, operates under ICE's enforcement umbrella. A $38.5 billion allocation over four years represents a substantial increase in the agency's capacity to pursue compliance actions — and FDNS site visits to Indian-staffed IT consulting firms have already been rising.

## What happens next

If the Senate passes the amended bill — which Republican leaders are confident will happen by the end of the week — it returns to the House for reconciliation with the version that chamber passed in May. The final product will then go to Trump's desk. Given the president's vocal support for enforcement spending, a veto is not a realistic scenario.

The practical effect for Indian visa holders: more enforcement officers, more compliance checks, more scrutiny of visa petitions, and more funding for the deportation infrastructure that serves as the backstop for every denied extension or revoked status. The $70 billion does not change the law. It changes the capacity to enforce it."""

# Image for Article 2: US Capitol from Pexels
print("📸 Sourcing image for Article 2 (Senate)...")
try:
    img2_url = "https://images.pexels.com/photos/32386663/pexels-photo-32386663.jpeg?auto=compress&cs=tinysrgb&w=1200"
    img2_bytes = download_image(img2_url)
    art2_img = upload_to_supabase(img2_bytes, f"{art2_id}.jpg")
    art2_caption = "The United States Capitol building in Washington, D.C., where the Senate is debating $70 billion in immigration enforcement funding"
    art2_attribution = "Pexels"
    print(f"  ✅ Uploaded: {art2_img}")
except Exception as e:
    print(f"  ⚠ Image failed: {e}")
    art2_img = ""
    art2_caption = ""
    art2_attribution = ""


# ── INSERT ARTICLES ────────────────────────────────────────────────

articles = [
    {
        "id": art1_id,
        "headline": "One Hundred and Eighteen Days — The EB-5 Deadline That Could Save Your Green Card",
        "subheadline": "Indian H-1B holders are rushing to file investor visa petitions before September 30, when grandfathering protections expire and the $800,000 threshold begins its march toward $950,000.",
        "slug": art1_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indian nationals hold 72% of H-1B visas and face decades-long EB-2/EB-3 green card backlogs. The EB-5 investor visa offers a path to employer-independent permanent residency — but the grandfathering deadline of September 30, 2026, is the last chance to lock in the $800,000 investment minimum and full statutory protection.",
        "tags": ["eb5", "green-card", "h1b", "investor-visa", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Golden Gate Global — EB-5 Update 2026-2027", "url": "https://3gfund.com/eb-5-visa-update-2026-2027/"},
            {"name": "CanAm Enterprises — The 2026 EB-5 Deadline", "url": "https://canamenterprises.com/the-2026-eb-5-deadline-what-investors-must-know/"},
            {"name": "Fragomen — EB-5 Regional Center Program Pathway", "url": "https://www.fragomen.com/insights/despite-eb-5-retrogression-for-indian-nationals-eb-5-regional-center-program-provides-a-promising-pathway.html"},
            {"name": "EB5Investors.com — U.S. Immigration Shifts Spark EB-5 Surge", "url": "https://eb5investors.com/eb5-news/us-immigration-shifts-spark-surge-in-eb5-interest/"},
            {"name": "StudentEB5 — H-1B Layoff Survival Guide", "url": "https://business.am-news.com/am-news/article/s-1685"}
        ]),
        "score_total": 82,
        "status": "published",
        "published_at": now,
        "image_url": art1_img,
        "image_caption": art1_caption,
        "image_attribution": art1_attribution,
        "body": art1_body,
        "is_editorial": False,
    },
    {
        "id": art2_id,
        "headline": "Seventy Billion Dollars and a Vote-a-Rama — The Enforcement Machine the Senate Is Building Today",
        "subheadline": "The Senate advanced a $70 billion immigration enforcement package 53-46 on Wednesday. Thursday's amendment marathon will determine what the final bill looks like — and how much more scrutiny Indian visa holders will face.",
        "slug": art2_slug,
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "The $38.5 billion ICE allocation directly funds the FDNS site visit programme and workplace compliance operations that disproportionately target H-1B-dependent IT firms with large Indian workforces. More funding means more officers, more visits, and more scrutiny of visa petitions and extensions.",
        "tags": ["senate", "reconciliation", "ice", "enforcement", "h1b", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Associated Press via Audacy", "url": "https://www.audacy.com/national-news/senate-begins-voting-on-funding-immigration-enforcement"},
            {"name": "New York Post", "url": "https://nypost.com/2026/06/04/us-news/senate-votes-to-advance-70b-plan-to-fund-ice-border-patrol/"},
            {"name": "Bloomberg Law — BGOV Bill Analysis S. 2", "url": "https://news.bloomberglaw.com/daily-labor-report/bgov-bill-analysis-s-2-immigration-border-reconciliation-bill"},
            {"name": "Bloomberg Law — Mullin Signals Flexibility", "url": "https://news.bloomberglaw.com/daily-labor-report/homelands-mullin-signals-flexibility-on-100000-h-1b-visa-fees"}
        ]),
        "score_total": 80,
        "status": "published",
        "published_at": now,
        "image_url": art2_img,
        "image_caption": art2_caption,
        "image_attribution": art2_attribution,
        "body": art2_body,
        "is_editorial": False,
    },
]

print("\n📝 Inserting articles...")
for art in articles:
    try:
        result = sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print("\n🏁 Done.")
