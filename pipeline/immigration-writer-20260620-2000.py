#!/usr/bin/env python3
"""Immigration writer 2026-06-20 20:00 UTC — 2 fresh articles.
Article 1: B-1/B-2 visa bond pilot (50 countries, India spared, Nepal/Bangladesh/Bhutan on list)
Article 2: 2025 naturalization civics test (128 bank, 20 asked, 12 to pass)
"""
import os, json, uuid, datetime, subprocess, sys

# --- env ---
def load_env(path):
    env = {}
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    return env

sb = load_env(os.path.expanduser('~/.env.supabase'))
SUPABASE_URL = sb['SUPABASE_URL']
SERVICE_KEY = sb['SUPABASE_SERVICE_ROLE_KEY']

now = datetime.datetime.now(datetime.timezone.utc)
now_iso = now.isoformat()

# ---------------- ARTICLE 1 ----------------
a1_body = """The United States is quietly building a financial wall around its tourist-visa system, and while India has so far been left off the list, the diaspora is far from untouched.

Since August 2025, the State Department has run a B-1/B-2 "visa bond" pilot that requires applicants from designated countries to post a refundable bond of **$5,000, $10,000, or $15,000** before a business or tourist visa is issued. In March 2026 the program quietly ballooned to **50 countries**, adding twelve nations — Cambodia, Ethiopia, Georgia, Grenada, Lesotho, Mauritius, Mongolia, Mozambique, Nicaragua, Papua New Guinea, Seychelles, and Tunisia — effective April 2.

For Indian passport holders, the headline is reassuring: **India is not on the list.** But three of India's closest neighbors are — **Nepal, Bangladesh, and Bhutan** — and that has real consequences for families woven across South Asia.

## Context & Background

The bond pilot was created through a State Department temporary final rule pitched as a tool to curb visa overstays. The logic is blunt: travelers from countries with high overstay rates must put money on the table, refundable only if they leave the United States on time and through approved channels. Travelers subject to a bond must also enter and exit through a **commercial airport** with U.S. Customs and Border Protection facilities — no land crossings, no charter flights, no seaports.

The list has grown in waves: Malawi and Zambia first in August 2025, a large expansion through the autumn and January 2026, and the latest twelve in spring. Several listed countries are also covered by the administration's travel ban, meaning their nationals cannot get a B visa at all, bond or no bond.

## Current Developments

The pilot is currently authorized only **through August 5, 2026**, which means the program is approaching a decision point: let it lapse, extend it, or — the possibility that worries immigration lawyers — expand it again to larger source countries.

For now, India's exclusion reflects its standing as a high-volume, comparatively low-overstay visa market. Indians remain among the largest recipients of U.S. visitor visas, and a bond requirement on Indian tourists would be both administratively enormous and diplomatically charged.

## Diaspora Impact

The catch for the Indian-American community is family geography. Many NRI households include relatives, in-laws, and elderly parents who hold **Nepali, Bangladeshi, or Bhutanese** passports. A daughter-in-law from Kathmandu, a grandparent from Dhaka, a cousin from Thimphu — any of them now faces a $5,000-to-$15,000 cash hurdle simply to attend a wedding, a graduation, or the birth of a grandchild in the United States.

The bond is refundable, but the cash-flow burden is immediate and steep, and the airport-only entry rule complicates travel for those who would otherwise route through land borders or regional hubs. For mixed-nationality families, the program turns a routine visit into a financial event.

There is also a signaling effect. Immigration attorneys read the steady expansion of the bond list as a template the administration could extend, and families with relatives in the affected countries are advising travelers to plan visits — and budgets — well in advance.

## What's Next

Watch the **August 5 sunset date**. If the State Department renews the rule, the question becomes whether the list stays at 50 or grows. For Indian-American families, the practical advice is unchanged but newly urgent: confirm the passport nationality of every visiting relative against the current list at travel.state.gov before booking, and budget for a bond if a relative travels on a Nepali, Bangladeshi, or Bhutanese document.

India dodged this wall. Its neighbors did not — and in diaspora households, that distinction lands at the dinner table."""

# ---------------- ARTICLE 2 ----------------
a2_body = """The path to a U.S. passport just got measurably harder, and for the Indian-American community — among the largest groups naturalizing each year — the change lands squarely on kitchen tables where parents and grandparents are studying for the citizenship interview.

As of **October 20, 2025**, anyone filing Form N-400 must take the redesigned **2025 Naturalization Civics Test**. The new exam draws from a bank of **128 questions** — up from 100 — and the officer now asks **20 questions** instead of 10, with applicants needing **12 correct** to pass instead of 6. The math is unforgiving: the number of questions you must answer correctly has doubled.

## Context & Background

The civics test is the oral history-and-government portion of the naturalization interview, administered one-on-one by a USCIS officer. Under the 2008 test still used for earlier filings, an applicant faced up to 10 questions and passed at 6 correct. The 2025 version reinstates a format first introduced in 2020, with modifications, under **Executive Order 14161**, which directs the Department of Homeland Security to strengthen "assimilation and civic preparedness" among new citizens.

About **75% of the 128 questions** are carried over from the 2008 test, some verbatim; the remaining quarter are new, and some older questions were dropped. The test remains oral, with no multiple choice, and the officer stops once the applicant either reaches 12 correct or misses 9.

## Current Developments

The redesign does not arrive in isolation. USCIS has simultaneously broadened its **"good moral character" review** and resumed **neighborhood investigations** of certain naturalization applicants — steps that, taken together, signal heightened scrutiny across the entire citizenship pipeline, not just the test itself.

Filing date is the dividing line. Applicants who filed **before October 20, 2025** — including those with pending cases — still take the easier 2008 test. Those filing on or after that date take the new exam. The long-standing **65/20 special consideration** survives: applicants aged 65 or older with at least 20 years as a permanent resident still take a 10-question version and pass at 6 correct.

## Diaspora Impact

Indians consistently rank among the top nationalities receiving U.S. citizenship each year, and the green-card-to-citizenship journey is a defining milestone for the community. For many families, the people now facing the harder test are **elderly parents** who immigrated later in life, sponsored by adult children — exactly the cohort for whom oral English and a doubled question count are most daunting.

The 65/20 carve-out shields the oldest, longest-settled green-card holders, but it leaves a large middle group exposed: parents in their 50s and early 60s, recently sponsored, who must now prepare for a 20-question oral exam in English. Community organizations and immigration attorneys report rising demand for citizenship-prep classes, and families are starting study earlier and leaning on USCIS's updated practice materials.

There is a strategic wrinkle, too. Because the cutoff is the **filing date**, some prospective applicants who were eligible before October 2025 may regret not filing sooner under the gentler rules — a reminder that in immigration, timing is often everything.

## What's Next

USCIS continues to publish updated study guides for the 2025 test while keeping 2008 materials available during the transition. For diaspora families, the practical playbook is clear: confirm which test applies based on filing date, start preparation well ahead of the interview, and budget extra study time for the doubled question count. With median naturalization processing still running months, the interview may feel distant — but the study clock starts now."""

def wc(t):
    import re
    return len(re.findall(r"\\w+", t))

print("A1 words:", wc(a1_body))
print("A2 words:", wc(a2_body))

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "U.S. Tourist-Visa Bond Wall Hits 50 Countries: India Spared, But Nepal and Bangladesh Aren't",
        "subheadline": "A refundable $5,000-$15,000 bond now gates B-1/B-2 visas from 50 nations. India is off the list, but NRI families with relatives in Nepal, Bangladesh, and Bhutan face a steep new hurdle before a single visit.",
        "slug": "visa-bond-pilot-50-countries-india-spared-nepal-bangladesh-bhutan-nri-families-20260620",
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "India is excluded from the U.S. visa bond list, but many NRI households include relatives on Nepali, Bangladeshi, or Bhutanese passports who now face a $5,000-$15,000 refundable bond and airport-only entry to visit family in the U.S.",
        "tags": ["visa bond", "B-1/B-2", "State Department", "Nepal", "Bangladesh", "Bhutan", "tourist visa", "NRI", "visa overstay"],
        "urgency": "high",
        "sources": json.dumps([
            {"title": "United States: State Department Adds Countries to B-1/B-2 Visa Bond Pilot Program", "url": "https://www.fragomen.com/insights/united-states-state-department-adds-countries-to-b-1-b-2-visa-bond-pilot-program.html", "publisher": "Fragomen"},
            {"title": "State Department's Visa Bond Program: 12 New Countries Added to the List", "url": "https://ogletree.com/insights-resources/blog-posts/state-departments-visa-bond-program-12-new-countries-added-to-the-list/", "publisher": "Ogletree Deakins"},
            {"title": "Countries Subject to Visa Bonds", "url": "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/visa-bond.html", "publisher": "U.S. Department of State"}
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "image_url": "https://images.pexels.com/photos/8061949/pexels-photo-8061949.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "Applicants from 50 countries must now post a refundable bond before a U.S. visitor visa is issued.",
        "image_attribution": "Photo by Borys Zaitsev / Pexels",
        "body": a1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "The U.S. Citizenship Test Just Got Twice as Hard — and Indian Families Are Feeling It",
        "subheadline": "The 2025 civics test draws from 128 questions, asks 20, and requires 12 correct to pass. For NRI parents naturalizing later in life, the doubled bar is reshaping how families prepare.",
        "slug": "2025-naturalization-civics-test-128-questions-20-asked-indian-families-citizenship-20260620",
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians are among the largest groups naturalizing each year. The redesigned 2025 civics test doubles the questions asked and the number needed to pass, hitting elderly NRI parents sponsored by adult children hardest while a 65/20 carve-out shields only the oldest.",
        "tags": ["naturalization", "civics test", "USCIS", "citizenship", "N-400", "Executive Order 14161", "NRI", "green card"],
        "urgency": "medium",
        "sources": json.dumps([
            {"title": "Chapter 2 - English and Civics Testing (Policy Manual Vol. 12, Part E)", "url": "https://www.uscis.gov/policy-manual/volume-12-part-e-chapter-2", "publisher": "USCIS"},
            {"title": "Study for the Test", "url": "https://www.uscis.gov/citizenship/find-study-materials-and-resources/study-for-the-test", "publisher": "USCIS"},
            {"title": "USCIS Announces the 2025 Naturalization Civics Test: What You Need to Know", "url": "https://wolfsdorf.com/uscis-announces-the-2025-naturalization-civics-test/", "publisher": "WR Immigration"}
        ]),
        "score_total": 78,
        "status": "review",
        "is_editorial": False,
        "published_at": now_iso,
        "image_url": "https://images.pexels.com/photos/8846754/pexels-photo-8846754.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
        "image_caption": "New citizens at a naturalization ceremony; the redesigned 2025 civics test raises the bar for applicants filing on or after October 20, 2025.",
        "image_attribution": "Photo by Mikhail Nilov / Pexels",
        "body": a2_body,
    },
]

# Insert via curl (PostgREST)
inserted = []
for art in articles:
    payload = json.dumps(art)
    cmd = [
        "curl", "-s", "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        "-H", f"apikey: {SERVICE_KEY}",
        "-H", f"Authorization: Bearer {SERVICE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: return=representation",
        "-d", payload,
    ]
    res = subprocess.run(cmd, capture_output=True, text=True)
    print("=" * 60)
    print("SLUG:", art["slug"])
    print("HTTP body:", res.stdout[:600])
    if res.stderr:
        print("STDERR:", res.stderr[:300])
    try:
        parsed = json.loads(res.stdout)
        if isinstance(parsed, list) and parsed and parsed[0].get("id"):
            inserted.append(parsed[0]["slug"])
            print("OK inserted")
        else:
            print("WARN: unexpected response")
    except Exception as e:
        print("Parse error:", e)

print("\\nINSERTED:", inserted)
