#!/usr/bin/env python3
"""Immigration writer — 2026-07-11 19:00 PT run. Third article: FY2027 wage-weighted lottery results."""

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
    return slug[:70].rstrip('-') + "-20260711"


article3_body = """The first season of the wage-weighted H-1B lottery is over. The petition filing window closed on June 30. The numbers are now clear enough to see what the new system has done, and the answer is: exactly what its designers intended. It rewarded higher salaries. It punished the entry-level model. And it hit Indian IT consulting harder than any other segment of the programme.

## A 38.5 Per Cent Drop

USCIS received 211,600 properly submitted H-1B registrations for fiscal year 2027 — down from 343,981 the year before. That is a 38.5 per cent decline, the sharpest single-year contraction in the programme's recent history.

Part of that drop reflects the beneficiary-centric system that DHS finalised in 2024, which stopped employers from boosting a single worker's odds by filing multiple registrations through different companies. The old game — where a candidate could appear in the lottery five times through five staffing agencies — is dead.

But the bigger shift is the weighted selection itself. Under the new rules, which took effect on February 27, each registration is entered into the lottery pool a number of times proportional to its wage level. A Level IV role (fully competent, top of the pay range) gets four entries. Level III gets three. Level II gets two. Level I — the entry-level category where most fresh graduates and consulting-firm placements land — gets one.

The math is brutal. DHS estimates that a Level IV registration now has roughly a 61 per cent chance of being selected. Level I: about 15 per cent. Under the old random system, everyone had roughly 30 per cent odds, regardless of salary. The same visa. Radically different chances of getting it.

## Who the System Was Built Against

Indian nationals receive approximately 70 per cent of all H-1B approvals. The wage-weighted model does not target them by name, but it targets the structure of how Indian IT firms have used the programme for decades.

The Indian IT consulting model — Infosys, TCS, Wipro, HCL, Tech Mahindra — was built on placing large numbers of workers at client sites, often at Level I or Level II wages. That model is what mass-registration strategies were designed around: file hundreds or thousands of registrations, accept the ~30 per cent odds per person, and staff enough winners to fill the pipeline.

The weighted system inverts that equation. Fewer registrations, higher wages, and one-entry-per-person combine to make the volume strategy uneconomic. Moody's has estimated that major Indian IT firms face $100 to $250 million in additional costs from the combined effect of wage weighting, the $100,000 filing fee for certain consular H-1Bs, and tighter third-party placement rules.

India's top five IT companies cut 7,389 jobs in FY2026 — not primarily because of the H-1B changes, but because the business model that depended on low-cost placement is being squeezed from multiple directions simultaneously.

## The US Advanced Degree Advantage

The other striking data point: 71.5 per cent of selected FY2027 applicants hold a US master's degree or higher. A year earlier, that figure was 57 per cent.

This matters enormously for Indian students making education decisions. A US graduate degree — once a nice-to-have that slightly improved H-1B odds through the separate master's cap — now offers a compounding advantage. Graduates who completed advanced degrees at US universities tend to land in higher-paying roles, which means higher wage levels, which means more lottery entries.

The flipside is rough. An Indian student who completes a bachelor's degree, enters OPT, and gets sponsored for an H-1B at an entry-level salary now faces a 15 per cent selection probability in a system where a senior colleague down the hall has a 61 per cent chance. Same programme, same law, wildly different access.

## What This Means for Indian Professionals

The H-1B is not closed to Indian workers. But it is no longer a volume game, and it is no longer neutral to salary. Three adjustments are now effectively mandatory for anyone serious about the H-1B route:

**Negotiate salary first, visa second.** Under the old system, getting sponsored mattered more than how much the role paid. Now, the wage level is part of the lottery odds. A Level II salary instead of Level I does not just mean more money — it literally doubles a candidate's entries in the draw.

**Treat the H-1B as one path, not the only path.** STEM OPT can buy time. Cap-exempt positions at universities and research institutions sit outside the lottery entirely. O-1 extraordinary ability visas remain above 90 per cent approval rates. And as this publication reported earlier this week, EB-1A self-petitions are surging — though those, too, are getting harder to win.

**Document everything from Day One.** The beneficiary-centric system and the post-selection compliance pressure mean that every detail — job title, SOC code, wage level, worksite, passport data — must be consistent from registration through the final petition. USCIS now cross-references registration data against the actual filing. A mismatch is a red flag. In the current enforcement environment, red flags trigger site visits.

## The Bigger Picture

For the roughly 1.43 lakh Indian nationals who registered for FY2027, these numbers are not abstract policy. They represent the difference between staying in the United States and not. The weighted system adds a new layer of selection pressure on top of the green card backlogs, the H-4 EAD clampdown, the Duration of Status changes for students, and the fraud investigation that Vice President Vance announced this week.

The H-1B pathway still works. But the era of treating it as a low-cost, high-volume pipeline — the era that built India's $250 billion IT export industry — is definitively over. What replaced it rewards individual merit, higher compensation, and stronger documentation. Whether that is fairer or merely more expensive depends on where you sit in the system. For most Indian applicants, it is both."""

article3 = {
    "id": str(uuid.uuid4()),
    "headline": "The First Wage-Weighted H-1B Lottery Is Over. Here Is What It Did to Indian Applicants",
    "subheadline": "Registrations dropped 38.5 per cent. Entry-level odds halved to 15 per cent. US master's degree holders surged to 71.5 per cent of selections. The numbers are in, and they reshape every assumption Indian professionals held about the H-1B path.",
    "slug": make_slug("wage-weighted-h1b-lottery-fy2027-results-indian-impact"),
    "category": "immigration",
    "vertical": "immigration",
    "diaspora_angle": "The first wage-weighted H-1B lottery cut entry-level selection odds in half and shrank total registrations by 38.5 per cent — reshaping the visa pathway that 70 per cent of Indian professionals depend on and forcing a strategic rethink from salary negotiation to alternative visa routes.",
    "tags": ["h1b", "wage-weighted-lottery", "fy2027", "indian-it", "uscis", "immigration", "visa-lottery"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "VisaVerge", "url": "https://www.visaverge.com/news/h-1b-lottery-shifts-in-fiscal-year-2027-favoring-us-masters-degree-holders/"},
        {"name": "Town Post", "url": "https://townpost.in/h-1bs-random-lottery-is-dead-higher-salaries-just-won/"},
        {"name": "Collegedunia", "url": "https://collegedunia.com/usa/article/fy2027-h1b-wage-lottery-results-what-indian-opt-students-must-know"},
        {"name": "Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1801714/what-recent-uscis-data-means-for-eb-2-niw-eb-1a-petitioners"}
    ]),
    "score_total": 80,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/1181404/pexels-photo-1181404.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=650&w=940",
    "image_caption": "Technology professionals collaborating in a modern office workspace",
    "image_attribution": "Pexels",
    "body": article3_body
}

try:
    sb_post("p2_articles", article3)
    print(f"✅ {article3['slug']}")
except Exception as e:
    print(f"❌ {article3['slug']}: {e}")
