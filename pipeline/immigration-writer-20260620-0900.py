#!/usr/bin/env python3
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

article1_body = """The July 2026 Visa Bulletin landed this week with the line Indian green-card applicants had been dreading for months. EB-2 India is now marked "Unavailable" — the letter "U" where a date should be — meaning no employment-based second-preference visas can be issued to Indian nationals for the rest of fiscal 2026, which runs through September 30. It is the bluntest possible signal: the per-country allotment for the year is spent, and the queue simply stops moving.

This is not a surprise so much as a confirmation. The State Department warned back in May, when it announced EB-2 India had hit its annual numerical limit, that the category could go dark before the fiscal year closed. June's bulletin had already retrogressed EB-2 India by nearly a year. July finishes the job.

## What actually changed in July

For Indian applicants, the bulletin reads like a list of doors closing. EB-2 India: Unavailable. EB-1 India also retrogressed — the Final Action Date moved backward to October 15, 2022, a two-month slide from June, and analysts had flagged EB-1 India as a growing pressure point as more applicants pile into what was once the fastest category. EB-3 India inched forward to a priority date of January 1, 2014, an advance of barely half a month, which is less a lifeline than a reminder of how glacial the alternative path remains.

Crucially, USCIS confirmed that employment-based adjustment-of-status filers must continue using the more restrictive Final Action Dates chart — not the Dates for Filing chart — to determine I-485 eligibility in July. That distinction matters enormously: it means many Indians whose priority dates look "current" on the friendlier chart still cannot file. Family-sponsored applicants, by contrast, may use the Dates for Filing chart, and saw a five-month leap in the F1 category.

## Why fiscal-year math keeps punishing Indians

The pattern is structural, not accidental. The federal fiscal year ends September 30, and in its final third the government rations visa numbers tightly to avoid blowing past the annual per-country ceiling — roughly seven percent of the worldwide total for any single country. India, with the deepest employment-based backlog of any nation, exhausts its slice first, then waits for the October reset to claw back a few dates.

So the realistic read for affected Indians is this: EB-2 India will almost certainly stay "Unavailable" until the October 2026 bulletin, when fiscal 2027 numbers free up and dates should jump forward again — though where they land is anyone's guess. EB-5, the investor category, remains one of the few lanes still showing movement, with the rural and high-unemployment set-asides current for all countries, which is why immigration lawyers keep nudging clients with capital toward it.

## What this means for Indian Americans

If you are an Indian professional on an H-1B with an EB-2 priority date, July changes nothing about your underlying place in line — but it freezes the practical reality of getting the green card. You cannot file or have an I-485 approved in this category right now. For people weighing a job change, that frozen status complicates the calculus around portability and advance parole, and anyone planning international travel should confirm their documents and re-entry posture before booking.

The deeper frustration is familiar to every Indian family that has lived inside this system: the backlog is now measured not in months but in administrative eras. A worker with an EB-2 priority date from the early 2010s is watching the category go dark entirely, while rest-of-world EB-2 stays current. The per-country cap, designed in a different demographic age, lands hardest on the largest, most qualified applicant pool in the country.

There are still moves on the board. Some applicants with EB-3 priority dates earlier than their EB-2 dates may benefit from a downgrade, since EB-3 India is at least advancing. Those with the means and risk tolerance are looking hard at EB-5. And everyone else is doing what backlogged Indians have done for fifteen years — waiting for October, and hoping the reset is generous.

The one certainty is the calendar. Fiscal 2026 ends September 30. Until then, for EB-2 India, the line does not move."""

article2_body = """For two decades, an H-1B worker in the United States who needed a fresh visa stamp had exactly one option: leave the country, fly to a consulate abroad — usually back home in India — and hope the appointment, the wait, and the re-entry all went smoothly. That last part has stopped being a safe assumption. Now Washington is preparing to bring a piece of the process back onto American soil, and it is aiming the first round squarely at Indians.

The State Department is set to launch a domestic visa renewal pilot in December, allowing a limited set of H-1B holders to renew their visas inside the United States rather than travelling overseas. Julie Stufft, the deputy assistant secretary for visa services, said the program will issue 20,000 visas over an initial three-month window, and that "the vast majority of those will be Indian nationals living in the US." The plan, referenced in a recent India-US joint statement, restores a stateside renewal option that was quietly discontinued in 2004.

## Who actually qualifies

The enthusiasm needs an immediate asterisk, because the eligibility rules are narrow. Based on the program's parameters, an applicant must be renewing an H-1B visa specifically — H-4 dependents and holders of L-1, O-1, E-3 and other categories are excluded from the pilot. The prior H-1B visa being renewed must have been issued by a US consulate in India between February 1, 2021 and September 30, 2021, or by a consulate in Canada between January 1, 2020 and April 1, 2023.

On top of that, the applicant must hold an approved, unexpired H-1B petition, be maintaining H-1B status, have most recently entered the country in that status, qualify for an interview waiver, have previously submitted ten fingerprints, and carry no visa ineligibility requiring a waiver. In other words, this is a tightly bounded test run, not a general amnesty from consular travel.

## Why it matters anyway

Even with the fences, the symbolism is large, and the practical relief is real for those who fit. The reason this lands so hard for Indians is the state of consular processing back home. Wait times at Indian posts have stretched to six, eight, even twelve months, with appointment dates at some consulates reportedly running as far out as 2027. Stufft herself acknowledged the backlog, calling the current waits "not what we need and not indicative of how we view India."

There is also a sharper hazard lurking behind any trip abroad right now. With the $100,000 fee attached to certain new H-1B petitions filed after September 21, 2025, immigration attorneys have been warning H-1B holders to avoid international travel where possible, because leaving and re-entering can expose workers to fees, stamping delays, and the general unpredictability of a tightened consular environment. A renewal that never requires leaving the country sidesteps that entire minefield.

## The fine print, and the hope

Stufft said a Federal Register notice would spell out the eligibility steps and the first tranche of applicants. That document is where the real answers live: how applications get submitted, how long domestic adjudication takes, and — most importantly to the hundreds of thousands of Indians not covered by the initial date windows — how quickly the program expands.

Because expansion is the whole point. A 20,000-visa pilot is a rounding error against the Indian H-1B population, and the narrow issuance-date windows mean most current visa holders will not qualify in round one. But the State Department has framed this as the opening move of a program "focused very much on India," with explicit intent to grow it. Setting up a dedicated consular division in Washington, as Stufft noted, is "not a small endeavor" — which is itself a signal that this is meant to be durable, not a one-off.

For an Indian professional who has spent years organising their life around a single fragile trip to Chennai or Hyderabad, the message is cautiously encouraging: the door to stateside renewal is reopening, even if only a crack for now. The smart move is to read the Federal Register notice the moment it publishes, check the issuance dates on your prior visa against the eligibility windows, and — if you qualify — be ready to file early, because 20,000 slots will not last long."""

articles = [
    {
        "id": str(uuid.uuid4()),
        "headline": "EB-2 India Just Went Dark for the Rest of the Year. The July Visa Bulletin Made It Official",
        "subheadline": "The State Department marked EB-2 India \"Unavailable\" through September 30, while EB-1 India retrogressed again — and USCIS is still forcing filers onto the stricter chart.",
        "slug": make_slug("eb2-india-unavailable-july-2026-visa-bulletin-eb1-retrogression"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians hold the deepest employment-based green-card backlog of any country, so a category going 'Unavailable' freezes the green-card path for thousands of Indian H-1B professionals until at least October.",
        "tags": ["visa bulletin", "eb-2 india", "green card", "uscis", "eb-1", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Capitol Immigration Law Group — July 2026 Visa Bulletin", "url": "https://www.cilawgroup.com/"},
            {"name": "VisaVerge — July 2026 Visa Bulletin Analysis", "url": "https://www.visaverge.com/"},
            {"name": "WR Immigration (Wolfsdorf) — June 2026 Visa Bulletin", "url": "https://wolfsdorf.com/"},
        ]),
        "score_total": 84,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/b0/United_States_Green_Card_%282023_edition%29.jpg",
        "image_caption": "A United States Permanent Resident Card (green card), 2023 edition",
        "image_attribution": "Wikimedia Commons",
        "body": article1_body,
    },
    {
        "id": str(uuid.uuid4()),
        "headline": "Stateside H-1B Visa Renewals Are Coming Back in December — and the First 20,000 Are Mostly for Indians",
        "subheadline": "The State Department's domestic renewal pilot lets a narrow band of H-1B holders skip the consular trip abroad, but the eligibility windows are tight and the slots are few.",
        "slug": make_slug("h1b-domestic-visa-renewal-pilot-december-2026-india-20000-slots"),
        "category": "immigration",
        "vertical": "immigration",
        "diaspora_angle": "Indians make up the largest skilled-worker group in the US and face the longest consular waits back home, so a domestic H-1B renewal option directly addresses one of the most stressful, travel-risk-laden parts of NRI working life.",
        "tags": ["h1b", "visa renewal", "state department", "consular", "stamping", "immigration"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian EYE — US to launch domestic visa renewal plan in December", "url": "https://theindianeye.com/"},
            {"name": "Fragomen — Domestic Visa Renewal Pilot FAQ", "url": "https://www.fragomen.com/"},
            {"name": "Tafapolsky & Smith LLP — State Department Pilot Program Announcement", "url": "https://www.tandslaw.com/"},
        ]),
        "score_total": 82,
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/15/United_States_Passport_Visa_Pages.jpg/1280px-United_States_Passport_Visa_Pages.jpg",
        "image_caption": "Visa pages inside a United States passport",
        "image_attribution": "Wikimedia Commons",
        "body": article2_body,
    },
]

for art in articles:
    wc = len(art["body"].split())
    try:
        sb_post("p2_articles", art)
        print(f"✅ {art['slug']} ({wc} words)")
    except Exception as e:
        print(f"❌ {art['slug']}: {e}")
