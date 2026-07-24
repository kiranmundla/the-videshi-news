#!/usr/bin/env python3
"""Immigration writer — July 8, 2026 1:00 PM batch"""
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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


# ─── ARTICLE 1: Credential fraud narrative against Indian doctors ────────────

article1_body = """A viral op-ed published on Wednesday accused Indian-trained doctors of posing a "public health and safety crisis" in the United States. The piece, which appeared in the Daily Caller, stitched together a handful of fraud cases, a former diplomat's contested allegations, and a USMLE cheating scandal to argue that America's reliance on Indian physicians has become dangerous. Within hours, it was circulating across immigration policy circles and diaspora WhatsApp groups alike.

The timing was not accidental. The essay landed the same week the Department of Labor Inspector General launched the Trump administration's first major H-1B and PERM fraud investigation, and just days after AAPI — the American Association of Physicians of Indian Origin — celebrated a federal court ruling that struck down the $100,000 fee on H-1B petitions. The credential fraud narrative is filling the space the fee debate vacated.

## What the op-ed claims

The Daily Caller piece, co-authored by former Ambassador Carla Sands and researcher Samantha Flanigan, opens with India's seizure of over 100,000 forged diplomas from 28 universities in December 2025. It then cites former consular officer Mahvash Siddiqui's claim that 80 to 90 per cent of H-1B visa applications from India she reviewed in Chennai between 2005 and 2007 involved "fraudulent documentation or unqualified applicants."

The piece names individual cases: a Harvard-affiliated cardiologist accused of fabricating research data, a West Virginia University professor whose medical school credentials could not be verified, a Louisiana paramedic who impersonated physicians for years, and a surgeon sued for installing a heart valve upside down in a 13-year-old patient. Taken together, the cases are alarming. Taken as representative of 250,000 international medical graduates working in America, they are something else entirely.

## What the data actually shows

The American healthcare system does not run on faith. International medical graduates must pass the United States Medical Licensing Examination — a three-step gauntlet that takes most candidates years to clear — complete a supervised residency programme, and obtain state licensure before touching a patient. These are not rubber stamps.

The numbers tell a more textured story than the op-ed allows. International medical graduates make up roughly 25 per cent of the active physician workforce in America. In rural and underserved communities, that figure climbs to 40 per cent. More than half of all internal medicine trainees are IMGs. They are disproportionately concentrated in specialties where shortages are most acute: geriatrics, nephrology, endocrinology, infectious disease.

When the federal government actually investigated H-1B fraud at scale, the results were not what the 80-per-cent headline suggests. In Operation Twin Shield, USCIS, ICE, and the FBI reviewed over 1,000 cases and conducted more than 900 site visits. Fraud or non-compliance was found in 275 cases. Only 42 individuals were referred to ICE. Four were apprehended. Less than five per cent of those investigated faced any immigration enforcement action.

## Why this matters to Indian Americans

The credential fraud narrative does not distinguish between a staffing company that fabricated job descriptions and a cardiologist who graduated from AIIMS and completed a residency at Johns Hopkins. It does not distinguish between a visa consultant in Hyderabad running a diploma mill and a nephrologist in rural Iowa who is the only specialist within 60 miles. By design, it does not need to.

AAPI President Dr. Amit Chakrabarty was blunt when the $100,000 fee was struck down last month: "This is not a political victory — it is a healthcare victory. It ensures that patients are not placed at risk due to policy barriers unrelated to clinical need."

The risk now is that the political conversation pivots from fees to fraud, and the target stays the same. Indian-origin physicians — many of them American citizens or permanent residents who trained, tested, and proved themselves within the American medical system — find their competence questioned not because of their performance, but because of their passport.

The United States is projected to face a shortage of 86,000 physicians by 2036. One in four of the doctors it has today trained abroad. The fraud that exists is real and should be prosecuted. But a handful of bad actors cannot be allowed to indict a quarter of the country's medical workforce. The patients who depend on them — disproportionately poor, rural, and underserved — cannot afford that arithmetic."""

article1 = {
    "id": str(uuid.uuid4()),
    "headline": "An Op-Ed Just Called Indian Doctors a Fraud Risk. Rural America Cannot Afford to Lose Them",
    "subheadline": "A viral Daily Caller piece stitches together individual fraud cases to indict 250,000 international medical graduates. Federal data tells a different story.",
    "slug": make_slug("indian-doctors-fraud-narrative-img-rural-healthcare"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "Indian-origin physicians make up 25% of the US doctor workforce and 40% in rural areas. A growing political narrative painting them all as fraud suspects threatens their careers and the communities that depend on them.",
    "tags": ["h1b", "healthcare", "indian-doctors", "img", "credential-fraud", "aapi", "immigration"],
    "urgency": "high",
    "sources": json.dumps([
        {"name": "Daily Caller", "url": "https://dailycaller.com/2026/07/08/opinion-indian-fraud-american-healthcare-h1b-carla-sands-samantha-flanigan/"},
        {"name": "AAPI / The Indian Eye", "url": "https://theindianeye.com/2026/06/17/aapi-applauds-court-ruling-blocking-100000-h-1b-physician-visa-requirement/"},
        {"name": "Reuters", "url": "https://www.reuters.com/legal/government/trumps-100000-h-1b-visa-fee-is-unlawful-us-judge-rules-2026-06-09/"},
        {"name": "Ahluwalia Law", "url": "https://ahluwalialaw.com/h-1b-immigration-fraud-what-employers-must-know-in-2026/"},
        {"name": "JAMA Network", "url": "https://jamanetwork.com/journals/jama/article-abstract/2830121"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/5452247/pexels-photo-5452247.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Medical professionals in a hospital setting",
    "image_attribution": "Pexels",
    "body": article1_body.strip()
}


# ─── ARTICLE 2: Hannah Dugan sentencing ──────────────────────────────────────

article2_body = """A former Milwaukee County judge walked out of a federal courtroom on Wednesday with a $5,000 fine, no prison time, and no apology. Hannah Dugan, 67, had been convicted of a felony for helping a Mexican immigrant use a back door to avoid Immigration and Customs Enforcement agents waiting outside her courtroom. The sentencing, which took place in the same city where Vice President JD Vance was simultaneously launching the administration's anti-fraud task force, distilled the contradictions of American immigration enforcement into a single afternoon.

## The incident

The facts were never in serious dispute. On April 18, 2025, Eduardo Flores-Ruiz, a Mexican national in the country illegally, was scheduled to appear before Dugan on misdemeanor assault charges. ICE agents had positioned themselves in a hallway outside her courtroom to arrest him on an immigration warrant.

Dugan directed Flores-Ruiz and his lawyer to walk through the "jury door" — a secured exit behind her bench that leads to a corridor a few feet further down the hall. He re-entered the main corridor in front of at least two federal agents, made it outside, and was arrested after a brief foot chase. The entire episode lasted minutes.

A jury convicted Dugan of obstructing a federal immigration proceeding in December. She was acquitted of a separate charge of concealing a person from arrest. Federal sentencing guidelines called for 15 to 21 months in prison.

## The sentence

U.S. District Judge Lynn Adelman, a Clinton appointee, rejected the prosecution's framework entirely. "This is the case of a good person, upset by immigration enforcement in this country, a sentiment widely shared, making a bad decision in the moment," he said.

Dugan, who had not spoken publicly about the case for more than a year, addressed the court. "I have been cast as both a scofflaw and a hero. I am neither. I am just a person who was trying to do my job," she said, occasionally choking up. She did not apologise.

The consequences outside the courtroom had already been severe. Dugan resigned the circuit judgeship she had held for nine years in January amid threats of impeachment from Republican state lawmakers. She has had to move. She withdrew from public life because of threats against her and her family. Two Marquette University law professors, including a former state Supreme Court justice, testified on her behalf.

## Two messages from one city

The sentencing took place blocks from where Vance was addressing an audience about the Trump administration's expanding anti-fraud campaign. Earlier that morning, Labor Department Inspector General Anthony D'Esposito had announced the administration's first major H-1B and PERM fraud investigation on national television, revealing that dozens of subpoenas had already been issued.

The juxtaposition was difficult to miss. In one part of Milwaukee, a judge was being sentenced for showing an immigrant a door. In another, the vice president was launching a campaign that will, by design, knock on many more.

## What this means for Indian Americans

The Dugan case involved a Mexican national, not an Indian visa holder. But the precedent extends well beyond one courtroom and one nationality.

Indian Americans interact with the immigration system at nearly every stage of their American lives — filing H-1B petitions, attending USCIS interviews, appearing at consulates for visa stamping, and showing up at federal buildings for naturalisation ceremonies. The current enforcement climate has expanded well beyond targeting those without legal status. Social media vetting now reaches back ten years. Adjustment of status — the process by which someone on an H-1B applies for a green card without leaving the country — has been reclassified as "extraordinary relief." The DOL is investigating employers for PERM fraud. Palantir's AI is cross-referencing H-1B filings for inconsistencies.

The Dugan case adds another dimension: the people within the system who might exercise discretion in an immigrant's favour now face personal consequences for doing so. That is not an abstract concern for a community that depends on consular officers, USCIS adjudicators, and immigration judges to exercise judgment on petitions that take years to process.

Dugan said she intends to return to civic life. "I will not let those minutes on April 18 define my life," she told the court.

For the immigration system she briefly disrupted, those minutes may end up defining quite a lot."""

article2 = {
    "id": str(uuid.uuid4()),
    "headline": "She Opened a Door for One Immigrant. It Cost Her a Career, a Home, and a Year of Silence",
    "subheadline": "Former Milwaukee judge Hannah Dugan was fined $5,000 and spared prison for obstructing ICE — on the same day JD Vance launched the administration's anti-fraud campaign in the same city.",
    "slug": make_slug("dugan-sentencing-milwaukee-ice-immigration-enforcement"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The Dugan case shows that even officials who exercise discretion in an immigrant's favour now face felony prosecution. For Indian Americans navigating H-1B renewals, green card adjudications, and naturalisation interviews, the chilling effect on those with power to help is a direct concern.",
    "tags": ["ice", "immigration-enforcement", "courthouse", "h1b", "dugan", "milwaukee", "vance"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/former-wisconsin-judge-be-sentenced-obstruction-immigration-case-2026-07-08/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/07/08/us/hannah-dugan-sentencing-milwaukee-ice/"},
        {"name": "Milwaukee Journal Sentinel", "url": "https://www.jsonline.com/story/news/crime/2026/07/08/former-milwaukee-judge-hannah-dugan-gets-fine-no-prison-for-obstructing-ice/77384291007/"},
        {"name": "Wall Street Journal", "url": "https://www.wsj.com/us-news/law/former-wisconsin-judge-spared-prison-time-for-obstructing-immigration-arrest-35b6f0e8"},
        {"name": "Fox Business", "url": "https://www.foxbusiness.com/politics/trump-admin-launches-first-major-h-1b-visa-fraud-investigation"}
    ]),
    "score_total": 75,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d5/Federal_Building_and_U.S._Courthouse%2C_Milwaukee%2C_WI_Aug_03.jpg",
    "image_caption": "The Federal Building and U.S. Courthouse in Milwaukee, where former Judge Hannah Dugan was sentenced",
    "image_attribution": "Wikimedia Commons",
    "body": article2_body.strip()
}


# ─── INSERT ──────────────────────────────────────────────────────────────────

articles = [article1, article2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
