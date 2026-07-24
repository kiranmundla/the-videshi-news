#!/usr/bin/env python3
import json, os, uuid, re, requests
from datetime import datetime, timezone
from pathlib import Path

# Load env
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
        "headline": "The F-1 'Stay as Long as You Study' Era Is Ending — and the Clock Now Starts the Day You Land",
        "subheadline": "A rule capping international students at a fixed term has cleared White House review. For Indian students — the largest cohort on US campuses — it turns an open-ended visa into one with an expiry date.",
        "slug": make_slug("us-f1-duration-of-status-fixed-term-rule-white-house-indian-students"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "Indians are the single largest group of international students in the US, and a fixed-term F-1 rule would force tens of thousands of them to file — and pay for — status extensions mid-degree instead of simply staying enrolled.",
        "tags": ["travel", "visa", "students", "F-1", "USA", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Bloomberg Law — Foreign Student Status Duration Limits Clear White House Review", "url": "https://news.bloomberglaw.com/daily-labor-report/foreign-student-status-duration-limits-clear-white-house-review"},
            {"name": "DHS — Notice of Proposed Rulemaking on Fixed Admission Period", "url": "https://www.dhs.gov/news/2025/08/27/dhs-proposes-change-admission-period-structure-f-j-and-i-nonimmigrants"},
            {"name": "The Indian Eye — Tighter student visa rules may impact Indians in US", "url": "https://theindianeye.com/"}
        ]),
        "score_total": 84,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/7972324/pexels-photo-7972324.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "International students walk across a university campus, a daily scene for the largest Indian student population abroad",
        "image_attribution": "Pexels",
        "body": """For four decades, the deal for an Indian student on an F-1 visa has been refreshingly simple: stay as long as you are genuinely enrolled and in good standing. That arrangement, known in immigration shorthand as "duration of status" (D/S), is now on the way out.

A Department of Homeland Security rule that would replace the open-ended D/S framework with a fixed admission period has cleared review at the White House Office of Management and Budget — the last bureaucratic step before a regulation is published. Once it appears in the Federal Register, the way international students count their time in America changes fundamentally.

## What actually changes

Under the current system, your I-20 governs your stay, and as long as you keep studying full-time and obey the rules, the calendar does not run against you. Under the proposed rule, F-1 students would instead be admitted for a fixed term — up to four years, or the length of the program, whichever is shorter. Anyone whose studies, Optional Practical Training (OPT), or Curricular Practical Training (CPT) run past that window would have to file a formal extension of stay with US Citizenship and Immigration Services (USCIS).

There is a sharper edge for some nationalities. The original DHS proposal limited students from countries with visa-overstay rates above 10% to a two-year term. India has historically sat below that threshold, which should keep most Indian students in the four-year bucket — but the exact final text, and the country list attached to it, will matter enormously and is not yet public.

## Why this lands hard on Indian students

Indians are the largest single nationality on American campuses, having overtaken China, with well over 300,000 students enrolled in recent years. A four-year clock is awkward for a population that disproportionately pursues STEM master's degrees followed by the 36-month STEM OPT extension — a path that routinely stretches past four years from the day of first entry.

The practical consequences are not abstract:

- **A new filing, and a new fee.** Continuing past your fixed term means an extension application to USCIS, with the processing times and costs that entails — replacing what used to be an automatic, paperwork-free continuation through your university's international office.
- **Less flexibility on OPT and CPT.** Immigration specialists warn the change strips out much of the room students currently have to adjust work authorization through their schools, pushing those decisions into formal USCIS adjudication.
- **Timing risk.** If an extension is pending when your fixed term lapses, you could be left in a gray zone over work authorization or even degree completion — the precise scenario that higher-education groups fought when a near-identical rule was floated in 2020 and later withdrawn.

## The wider squeeze

This rule does not arrive in a vacuum. Over the past year, thousands of F-1 students saw their status terminated over database flags, a multi-week pause hit visa interviews, and US foreign enrollment dropped for the first time in three years. The duration-of-status change is the structural piece layered on top of those disruptions — and unlike the others, it rewrites the baseline rules rather than tightening enforcement at the margins.

For NRI families, the message is concrete. If your child is heading to a US university this fall, build the assumption of a mid-degree status renewal into the plan: keep the I-20 and program end dates precise, treat the four-year mark as a hard checkpoint rather than a formality, and budget for an extension filing if the degree-plus-OPT timeline runs long. Students already in the pipeline should watch for the published rule and any grandfathering provisions, which is where the real detail — and the real relief, if any — will sit.

## What's next

The rule has cleared OMB but has not yet been formally published. Once it is, expect a comment window and, likely, legal challenges from universities and industry groups who argue it burdens the very STEM talent the US says it wants to keep. Until the final text lands, nothing has technically changed for a student already on an F-1. But the direction of travel is unmistakable: the era of the open-ended American student visa is closing, and the clock now starts the day you land."""
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Canada's Student-Visa Door Is Closing on Indians — Rejection Rates Are Up and the Money Bar Just Got Higher",
        "subheadline": "A 35% cap on study permits, a CAD 22,895 proof-of-funds floor and tougher scrutiny have cut Indian enrollment sharply. For NRI families weighing Canada against the US, UK and Australia, the math has changed.",
        "slug": make_slug("canada-student-visa-crackdown-indians-rejection-proof-of-funds-cap"),
        "category": "travel",
        "vertical": "immigration",
        "diaspora_angle": "India is Canada's single largest source of international students, so tighter caps, higher fund requirements and rising rejections hit Indian families harder than any other group planning to send children abroad.",
        "tags": ["travel", "visa", "students", "Canada", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — Indian applicants hit hard by Canada's crackdown on student visas", "url": "https://theindianeye.com/"},
            {"name": "IRCC — New International Student Program regulations", "url": "https://www.canada.ca/en/immigration-refugees-citizenship.html"},
            {"name": "Shiksha — Canada Student Visa Guide 2026 for Indian Applicants", "url": "https://www.shiksha.com/studyabroad/canada/"}
        ]),
        "score_total": 80,
        "status": "review",
        "published_at": now,
        "image_url": "https://images.pexels.com/photos/32449388/pexels-photo-32449388.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "A modern university library in Toronto, where Indian enrollment has fallen sharply under Canada's study-permit caps",
        "image_attribution": "Pexels",
        "body": """For a decade, Canada sold itself to Indian families with a three-word promise: study, work, stay. That pitch is now badly frayed. A combination of hard caps on study permits, a steep rise in the money students must prove they have, and visibly tougher scrutiny has driven Indian applications down — and rejections up — to a degree that is reshaping where the diaspora's children apply.

## The numbers behind the squeeze

Canada has cut its annual study-permit intake by roughly 35%, to about 360,000 approvals, a policy Ottawa has framed as temporary but which is biting now. The effect on the country's largest source of students is stark: the University of Waterloo, home to Canada's biggest engineering school, has seen a two-thirds drop in Indian enrollment over three to four years. The University of Regina and the University of Saskatchewan report similar declines.

The Indian Embassy in Ottawa has acknowledged the higher rejection rate while noting, pointedly, that issuing permits remains "Canada's prerogative." Around 230,000 Indian students remain enrolled across the country — still a huge cohort, but a shrinking one.

## What's actually harder now

Several rule changes stack on top of each other:

- **A much higher money bar.** Since September 2025, a single applicant must show access to **CAD 22,895** in living funds — on top of first-year tuition and travel costs. For a family of four, the requirement climbs past CAD 42,000. That is roughly ₹20 lakh for the student alone, before a rupee of tuition.
- **The fast track is gone.** The Student Direct Stream (SDS), which once sped up approvals for Indian applicants, was scrapped in late 2024. Everyone now applies through the regular academic stream, which demands a fuller financial history and a more convincing statement of "genuine intent" to study.
- **Provincial attestation letters.** Most undergraduate and diploma applicants now need a Provincial Attestation Letter (PAL) confirming a province has room for them. Master's and PhD students at public institutions are exempt — a deliberate tilt toward higher-degree applicants.
- **Tighter scrutiny of funds.** Consultants say officers no longer accept bank statements at face value. As one Canadian visa specialist put it, applicants increasingly have to show "where the money came from," not just that it exists.
- **Narrower work and PR pathways.** Post-graduation work permits have been pared back and partly redirected to encourage graduates to return home; spousal open work permits are now largely limited to partners of master's and doctoral students.

## Why this matters to NRI families

For Indian American and broader diaspora families, Canada has often been the pragmatic choice — closer culturally, historically friendlier on permanent residency, and cheaper than elite US private universities. That calculus is shifting. With processing times for India now running 8 to 12 weeks and an environment where, as one student-association founder observed, some rejected applicants are "happy they didn't come," the country no longer offers the near-guaranteed runway it once did.

The practical takeaways for families planning the 2026-27 cycle:

- **Front-load the finances.** Have the full CAD 22,895-plus-tuition figure documented well in advance, with a clear and traceable source for the funds. A last-minute lump-sum deposit is now a red flag, not a reassurance.
- **Favor the degrees Canada still wants.** Master's and PhD applicants at public universities sit outside the cap and the PAL requirement and retain the strongest work-permit terms. Undergraduate and private-college diploma routes carry the most risk.
- **Apply early and write a real SOP.** With the fast track gone, the statement of purpose and proof of genuine intent now carry decisive weight. Build at least four months of lead time before the course start date.
- **Keep a Plan B open.** The same families are increasingly hedging toward the UK, Australia and, despite its own tightening, the US. Canada is no longer a default — it is one option among several, and a more demanding one.

## What's next

Ottawa has called the cap a two-year measure and says it will reassess. But with a federal focus on housing strain and immigration integrity, few expect a quick return to the open-door years. For now, the smartest move for diaspora families is to treat a Canadian study permit as a competitive application to be won — not a formality to be completed."""
    }
]

inserted = []
for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
        inserted.append(art['headline'])
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")

print(f"\n{len(inserted)} article(s) inserted:")
for h in inserted:
    print(f"  - {h}")
