#!/usr/bin/env python3
"""NRI World Writer — 2026-07-10 09:00 PDT"""

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


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 1: Carnegie 2026 Indian American Attitudes Survey
# ──────────────────────────────────────────────────────────────────────

art1_body = """A new nationally representative survey of 1,000 Indian American adults paints the most detailed picture yet of a community caught between rising discrimination, fraying political loyalties, and a quiet recalibration of everyday life in the United States.

The 2026 Indian American Attitudes Survey (IAAS), conducted by the Carnegie Endowment for International Peace in partnership with YouGov, finds that 71 per cent of Indian Americans disapprove of Donald Trump's job performance one year into his second term — virtually identical to the numbers recorded at the end of his first term. Fifty-five per cent express *strong* disapproval.

## The partisan ground is shifting — but not where you'd expect

Indian Americans remain overwhelmingly Democratic, yet the grip is loosening. The share identifying as Democrats has slid from 52 per cent in 2020 to 46 per cent in 2026. Republican identification has ticked up modestly. But the biggest winner is the independent column: nearly one-third of Indian Americans now decline to claim either party, and moderates represent the single largest ideological bloc at 32 per cent.

The 2024 presidential election previewed this shift. Trump narrowed the once-comfortable 70–20 Democratic margin to roughly 60–30, with notable gains among young Indian American men. A year later, his support has softened — but Democratic backing has not bounced back commensurately. In a hypothetical 2024 rerun, Democratic support remains about ten points below its 2020 peak. Openness to a third-party candidate has grown.

"Claims of a wholesale realignment are overstated," the Carnegie researchers write. "But the softening is real."

## Discrimination is not just a data point — it is reshaping daily life

The survey's most striking findings concern not what Indian Americans think, but what they *do*. Nearly one-third — 31 per cent — report avoiding political discussion on social media out of fear of discrimination or racism directed at Indians. Twenty-one per cent say they have avoided leaving and re-entering the United States. The same share has stopped displaying political signs or bumper stickers. And 19 per cent report avoiding wearing Indian dress or attire in public.

These are not responses to isolated incidents. They are the accumulated weight of an atmosphere. A separate report by the Network Contagion Research Institute documented a troubling surge in anti-Indian content on X (formerly Twitter) in late 2025, with some weeks seeing over 800 posts containing slurs like "pajeet" and "dothead." The NCRI identified the United States as an "epicenter of anti-Indian digital racism."

The Carnegie survey itself records widespread perceptions of bias and frequent encounters with online racism among Indian Americans. However, since 2020, there has been no statistically significant change in the share reporting *direct, personal* experience with discrimination — suggesting that the current wave of hostility is more ambient than targeted, more digital than physical, but no less corrosive.

## The exit question

Fourteen per cent of Indian Americans say they have *frequently* thought about leaving the United States altogether; another 26 per cent have thought about it *occasionally*. The top reason cited is not discrimination — it is frustration with American politics, named by 58 per cent of those considering departure. Cost of living (54 per cent) and personal safety (41 per cent) follow.

Still, a clear majority do not plan to leave, and most continue to recommend the United States for employment. The impulse to go is real but not dominant. For most Indian Americans, the question is not whether to stay, but how to live differently while staying.

## What the diaspora is watching

The survey also probed Indian Americans' views on specific Trump administration immigration policies. Large majorities oppose arresting undocumented immigrants with no criminal record, conducting workplace immigration raids, deporting immigrants to third countries, ending birthright citizenship, and levying a proposed $100,000 fee on new H-1B visa petitions.

Immigration policy disapproval stands at 64 per cent overall. Among self-identified Republicans within the community, however, 76 per cent *support* the administration's immigration stance — a sharp internal divide that mirrors the polarisation in the broader American electorate.

The survey captures a community in flux: still prosperous, still engaged, still broadly liberal — but less certain of its political home, more guarded in its public expression, and quietly adjusting the terms of its American life. For 5.2 million people navigating the space between two countries and two identities, the turbulence is no longer abstract. It is personal.

---

*The 2026 IAAS was conducted between November 25, 2025, and January 6, 2026. The full report is available at the Carnegie Endowment for International Peace.*"""


art1 = {
    "id": str(uuid.uuid4()),
    "headline": "Seventy-One Per Cent Disapprove, Thirty-One Per Cent Have Gone Quiet on Social Media. Inside the Landmark Survey That Maps Indian America's Political Anxiety.",
    "subheadline": "The Carnegie Endowment's 2026 Indian American Attitudes Survey of 1,000 adults reveals a community whose partisan loyalties are loosening, whose daily habits are shifting under the weight of discrimination — and whose frustration with American politics now outranks fear of racism as the reason some consider leaving.",
    "slug": make_slug("carnegie-iaas-2026-indian-american-attitudes-survey-discrimination"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "The survey maps exactly how the 5.2-million-strong Indian American community is processing political volatility, online hate, and shifting identity — and how those forces are changing what they wear, where they travel, and whether they speak up in public.",
    "tags": ["nri", "diaspora", "indian-american", "discrimination", "politics", "survey", "carnegie-endowment"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Carnegie Endowment for International Peace", "url": "https://carnegieendowment.org/russia-eurasia/research/2026/02/indian-americans-in-a-time-of-turbulence-2026-survey-results"},
        {"name": "Network Contagion Research Institute / The Free Press", "url": "https://theindianeye.com"},
        {"name": "Carnegie Endowment — Indian Americans Still Lean Left", "url": "https://carnegieendowment.org"}
    ]),
    "score_total": 82,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://images.pexels.com/photos/16100484/pexels-photo-16100484.jpeg",
    "image_caption": "Indian community members gathered at an outdoor cultural event — the kind of public expression a growing share of Indian Americans say they are reconsidering",
    "image_attribution": "Pexels",
    "body": art1_body
}


# ──────────────────────────────────────────────────────────────────────
# ARTICLE 2: India's OCI Rule Overhaul 2026
# ──────────────────────────────────────────────────────────────────────

art2_body = """For years, renewing an Overseas Citizen of India card meant shuffling between consulate counters, printing documents in duplicate, and praying the system didn't eat your application. India just overhauled the entire process — and for five million OCI holders worldwide, the changes are substantial.

The Ministry of Home Affairs notified the Citizenship (Amendment) Rules, 2026 in May, introducing a fully digital framework for OCI registration, re-issuance, renunciation, and cancellation. The changes came into force immediately. Here is what every OCI holder needs to know.

## Everything is online now — no exceptions

All OCI applications must now be filed electronically through the redesigned portal at ociservices.gov.in. The old requirement to submit documents in duplicate is gone. The new portal, which replaces a system built in 2013, introduces a suite of features: auto-fill of profile details, a dashboard tracking completed and pending applications, an integrated payment gateway for those filing through Foreigners Regional Registration Offices (FRROs), in-built image cropping tools for uploading photos and signatures, and the ability to edit applications at any stage before final submission.

"The new OCI portal introduces enhanced functionality, advanced security, and a user-friendly experience for existing OCI cardholders and new users," the Ministry of Home Affairs said in a statement.

## The e-OCI is here

For the first time, India now issues an electronic OCI — the e-OCI — as either a replacement for or supplement to the physical card. All records are maintained digitally, meaning holders no longer need to carry a physical card as their primary proof of status. The move is expected to dovetail with India's biometric-enabled Fast Track Immigration Programme, which allows e-gate processing at Indian airports when holders provide biometric consent.

## New compliance requirements — and a fine for missing them

The overhaul is not all convenience. A new compliance mandate requires OCI holders to upload a copy of their new passport and a recent photograph to the portal each time a new passport is issued — until age 20, and once again after age 50. The upload must be completed within three months of receiving the new passport. Miss the window, and there is now a $25 fine (or the local-currency equivalent).

For OCI holders who obtained registration after age 20, there is no requirement to re-issue the physical card at all — a significant simplification of the old rules, which had caused widespread confusion about whether cardholders needed to "renew" at ages 20 and 50.

"This will remove the confusion to many OCI card holders on the process of renewing the card at the age of 20 and 50," said Dr. Thomas Abraham, Chairman of the Global Organization of People of Indian Origin (GOPIO International). "This will also encourage more overseas Indians to become OCIs and it will benefit India through their travel, business, and investment."

## Broader eligibility, stricter rules for minors

The revised rules expand eligibility. Notably, fifth- and sixth-generation Indian-origin Tamils in Sri Lanka can now apply for OCI status, where previously the scheme was limited to fourth-generation descendants.

Eligible foreign nationals can also now apply for an OCI card without completing the previously required six months of stay in India. If they hold a valid long-term visa and the requisite documents, they can submit their application soon after arrival.

On the other hand, the rules explicitly clarify that no minor may hold both an Indian passport and a foreign passport simultaneously — addressing a long-standing grey area around dual citizenship, which India does not permit.

## Spousal OCI holders face additional requirements

OCI holders who obtained their status as the spouse of an Indian citizen or another OCI cardholder must upload, along with the passport update, a declaration confirming that the marriage is still subsisting. This requirement applies each time a new passport is issued.

## What OCI holders should do now

The practical to-do list is short but urgent: bookmark ociservices.gov.in, check whether your current passport details are updated on the portal, and upload your latest photograph if you have received a new passport since the rules came into effect. If you are over 20 and under 50 and have already registered, there is likely nothing to do until your next passport renewal — but verify your status on the dashboard.

For the roughly 5 million OCI holders navigating life between two countries, the overhaul is overdue. The question now is whether the digital system performs as advertised — or whether the portal, like its predecessor, becomes another bottleneck in a process that was never designed for the scale of India's global diaspora.

---

*The Citizenship (Amendment) Rules, 2026 were published in the official gazette on May 1, 2026 and are in force. The new OCI portal is live at ociservices.gov.in.*"""


art2 = {
    "id": str(uuid.uuid4()),
    "headline": "India Just Overhauled the OCI Card System for Five Million Holders Worldwide. Here Is What Changed — and What You Need to Do.",
    "subheadline": "The Ministry of Home Affairs has introduced fully digital OCI applications, an electronic OCI card option, a $25 fine for non-compliance, and expanded eligibility — the biggest update to the programme since 2013.",
    "slug": make_slug("india-oci-card-overhaul-2026-digital-eoci-rules"),
    "category": "nri-world",
    "vertical": "nri-world",
    "diaspora_angle": "Every OCI holder abroad — from the tech worker in San Jose to the retiree in London — is affected by these rule changes. The new compliance requirements, especially the passport-update window and $25 fine, demand immediate attention from the diaspora.",
    "tags": ["nri", "diaspora", "oci-card", "india-policy", "citizenship", "digital-government"],
    "urgency": "medium",
    "sources": json.dumps([
        {"name": "Ministry of Home Affairs / Dainik Jagran English", "url": "https://english.dainikjagranmpcg.com"},
        {"name": "Fragomen Immigration Services", "url": "https://fragomen.com"},
        {"name": "Envoy Global", "url": "https://envoyglobal.com"},
        {"name": "The Indian EYE", "url": "https://theindianeye.com"}
    ]),
    "score_total": 78,
    "status": "review",
    "is_editorial": False,
    "published_at": now,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/d/d2/OCI_2021.jpg",
    "image_caption": "An Overseas Citizen of India card — India has now introduced a digital e-OCI alternative alongside the physical document",
    "image_attribution": "Wikimedia Commons",
    "body": art2_body
}


# ──────────────────────────────────────────────────────────────────────
# Insert
# ──────────────────────────────────────────────────────────────────────

articles = [art1, art2]

for art in articles:
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']}")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
