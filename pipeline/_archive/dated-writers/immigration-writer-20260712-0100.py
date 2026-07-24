#!/usr/bin/env python3
"""
Immigration article writer — July 12 2026, 01:00 AM PT batch.
Inserts 2 articles into Supabase with status="review".

Articles:
  1. USCIS Signature Rule (effective July 10, 2026)
  2. Americans First Immigration Act (Rep. Barry Moore's bill)
"""

import json
import os
import subprocess
import sys
from datetime import datetime, timezone

# ── Load env ──────────────────────────────────────────────────────
def load_env(path):
    env = {}
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                k, v = line.split('=', 1)
                env[k.strip()] = v.strip()
    return env

supabase = load_env('~/.env.supabase')
SUPABASE_URL = supabase['SUPABASE_URL']
SUPABASE_KEY = supabase['SUPABASE_SERVICE_ROLE_KEY']

# ── Articles ──────────────────────────────────────────────────────

ARTICLES = [
    # ── ARTICLE 1: USCIS Signature Rule ──
    {
        "headline": "USCIS Can Now Deny Your Filing Over an Invalid Signature — and Keep Your Fee",
        "subheadline": "A new rule effective July 10 gives the agency power to deny petitions with flawed signatures after acceptance, with no opportunity to correct the mistake. Immigration attorneys are sounding the alarm.",
        "slug": "uscis-signature-denial-rule-july-2026-20260712",
        "category": "immigration",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "score_total": 74,
        "image_url": "https://images.pexels.com/photos/4922356/pexels-photo-4922356.jpeg",
        "image_caption": "Travel documents — a new USCIS rule tightens signature requirements across all immigration filings",
        "image_attribution": "Pexels",
        "diaspora_angle": "Indian nationals file hundreds of thousands of immigration petitions each year — H-1B transfers, I-485 adjustments, EAD renewals. A signature deemed invalid under the new rule could mean a denied case and forfeited filing fees, with no chance to fix the error.",
        "sources": json.dumps([
            {"name": "Greenberg Traurig / Mondaq", "url": "https://www.mondaq.com/unitedstates/work-visas/1604802/uscis-announces-new-rule-on-invalid-signatures"},
            {"name": "Federal Register (DHS Final Rule)", "url": "https://www.federalregister.gov/documents/2026/05/11/2026-10241/signature-requirements-for-immigration-filings"},
            {"name": "Reddy Neumann Brown PC", "url": "https://www.rnlawgroup.com/uscis-signature-denial-rule-2026/"},
            {"name": "American Immigration Lawyers Association", "url": "https://www.aila.org/"}
        ]),
        "tags": ["uscis", "signature-rule", "immigration-policy", "h-1b", "green-card", "filing-requirements"],
        "urgency": "standard",
        "key_takeaways": json.dumps([
            "USCIS can now deny filings with invalid signatures after acceptance — previously it could only reject them at intake.",
            "Denied petitions lose all filing fees with no refund and no cure period.",
            "The rule covers all form types including H-1B petitions, I-485 adjustment of status, and EAD applications.",
            "Attorney-signed forms must include a valid G-28 on file; missing or mismatched G-28s can trigger denial.",
            "Immigration lawyers warn the rule creates a 'gotcha' mechanism with disproportionate consequences."
        ]),
        "body": """<!-- data-card -->
<div class="vdc-takeaways"><div class="vdc-takeaways-title">Key Takeaways</div><ul><li>USCIS can now deny filings with invalid signatures after acceptance — not just reject them at intake.</li><li>Denied petitions forfeit all filing fees with no refund.</li><li>There is no cure period — applicants cannot fix a signature problem once the denial is issued.</li><li>The rule applies to every immigration form, including H-1B, I-485, and EAD applications.</li><li>Immigration attorneys warn the change creates disproportionate consequences for minor errors.</li></ul></div>

A rule that took effect on July 10 gives USCIS a power it has never formally had: the ability to deny an immigration filing — after accepting it, cashing the fee, and assigning a receipt number — solely because the agency later determines the signature is invalid.

Previously, a signature problem caught at intake resulted in rejection. The filing was sent back, the fee returned, and the applicant could correct and refile. Under the new framework, USCIS can issue a denial at any stage of adjudication. A denial is a different animal: filing fees are forfeited, any associated employment authorisation or status tied to the pending petition may lapse, and the clock resets.

## What Counts as an Invalid Signature

The rule applies to wet-ink, electronic, and typewritten signatures. USCIS considers a signature invalid if it was not made by the person identified on the form, was affixed by someone lacking the authority to sign, or does not correspond to the signatory named on the petition. For attorney-signed filings — which account for the bulk of employment-based petitions — the signature must be backed by a properly executed Form G-28 (Notice of Entry of Appearance) already on file with the agency.

A missing G-28, a G-28 naming a different attorney than the one who signed the petition, or a G-28 that was filed for a different case could all be treated as signature defects under the rule's language.

## No Cure, No Refund

The most consequential aspect of the rule is what it does not include: a cure mechanism. Under existing practice for Requests for Evidence (RFEs), USCIS issues a notice and gives applicants a window — typically 30 to 87 days — to provide additional documentation. The signature rule provides no comparable opportunity.

"This is a 'gotcha' provision," said one immigration attorney quoted in a Greenberg Traurig advisory. "An applicant who makes an honest mistake on a signature — or whose attorney's G-28 has a discrepancy — gets the same outcome as someone who committed fraud. The proportionality is off."

Filing fees for employment-based petitions are substantial. An H-1B petition with premium processing now runs above $2,800. An I-485 adjustment of status application for a family can exceed $3,000. Forfeiting those fees over a procedural signature issue, without the chance to correct it, represents a meaningful financial hit.

## The Diaspora Impact

Indian nationals are the largest single group of employment-based immigration petitioners. In fiscal year 2025, they accounted for roughly 72 per cent of all H-1B approvals and a growing share of EB-1A and EB-2 NIW filings. The sheer volume of petitions means that even a small percentage of signature-related denials could affect thousands of Indian applicants.

The risk is compounded by the common practice of employer-sponsored filings, where HR departments or outside counsel handle paperwork on behalf of the beneficiary. A corporate immigration team managing dozens of simultaneous filings faces more surface area for a G-28 mismatch or an unsigned page to slip through.

https://x.com/USCIS

For applicants in H-1B status whose petitions are denied, the consequences extend beyond the lost fee. A denied H-1B transfer petition can leave an employee without valid work authorisation if their prior petition has expired. A denied I-485 can restart a process that, for Indian-born applicants in the EB-2 and EB-3 categories, already involves decade-long backlogs.

## What Applicants Should Do

Immigration attorneys are urging immediate action. Every signature page on every pending and future filing should be reviewed for completeness. G-28 forms should be audited to ensure the named attorney matches the person who actually signed the petition, and that each G-28 corresponds to the specific case — not a prior matter with the same client.

For self-filers — a growing category as more Indian professionals pursue EB-1A and NIW petitions without counsel — the recommendation is straightforward: sign every page that requires a signature, use the exact legal name that appears on your passport, and retain copies of every signed page before submission.

The rule was published in the Federal Register on May 11, 2026, with a 60-day effective date. USCIS has not yet issued operational guidance to its adjudicators on how the rule will be applied in practice — a gap that attorneys say adds uncertainty to an already high-stakes change.""",
    },

    # ── ARTICLE 2: Americans First Immigration Act ──
    {
        "headline": "A New Bill Would Scrap the Green Card System Entirely. Here Is What Would Replace It",
        "subheadline": "The Americans First Immigration Act proposes a points-based model for employment immigration, eliminates the diversity visa lottery, and restricts family-based categories — a direct threat to the pathways Indian professionals rely on.",
        "slug": "americans-first-immigration-act-points-system-bill-20260712",
        "category": "immigration",
        "vertical": "immigration",
        "status": "review",
        "is_editorial": False,
        "score_total": 76,
        "image_url": "https://images.pexels.com/photos/7651973/pexels-photo-7651973.jpeg",
        "image_caption": "The proposed Americans First Immigration Act would fundamentally restructure how the United States selects employment-based immigrants",
        "image_attribution": "Pexels",
        "diaspora_angle": "Indian professionals have spent years navigating the existing employment-based green card system — enduring decade-long backlogs in EB-2 and EB-3 categories. A points-based replacement could either accelerate or entirely block their paths depending on how the scoring weights shake out.",
        "sources": json.dumps([
            {"name": "Rep. Barry Moore Press Release", "url": "https://barrymoore.house.gov/media/press-releases/americans-first-immigration-act"},
            {"name": "NumbersUSA", "url": "https://www.numbersusa.com/news/americans-first-immigration-act-2026"},
            {"name": "Center for Immigration Studies", "url": "https://cis.org/"},
            {"name": "Forbes / Stuart Anderson", "url": "https://www.forbes.com/sites/stuartanderson/"}
        ]),
        "tags": ["green-card", "points-based-immigration", "employment-immigration", "diversity-visa", "family-immigration", "congress", "legislation"],
        "urgency": "standard",
        "key_takeaways": json.dumps([
            "The bill would replace the current employment-based green card system with a points-based model.",
            "Points would be awarded for education level, English proficiency, salary, age, and job offers.",
            "The diversity visa lottery — 55,000 green cards annually — would be eliminated entirely.",
            "Family-based immigration would be narrowed to spouses and minor children only.",
            "The bill requires employers to prove domestic recruitment efforts before sponsoring foreign workers.",
            "Backed by NumbersUSA and America First Policy Institute, but faces long odds in the current Congress."
        ]),
        "body": """<!-- data-card -->
<div class="vdc-takeaways"><div class="vdc-takeaways-title">Key Takeaways</div><ul><li>The Americans First Immigration Act would replace employment-based green cards with a points-based system.</li><li>Points are awarded for education, English proficiency, salary, age, and a qualifying job offer.</li><li>The 55,000-visa diversity lottery would be eliminated.</li><li>Family immigration would be restricted to spouses and minor children of U.S. citizens.</li><li>Employers would need to demonstrate failed domestic recruitment before sponsoring a foreign worker.</li><li>The bill has restrictionist backing but faces steep odds in a divided Congress.</li></ul></div>

Representative Barry Moore, a Republican from Alabama, has introduced legislation that would dismantle the employment-based green card system as it has existed for more than three decades and replace it with a points-based model. The bill, titled the Americans First Immigration Act, has drawn endorsements from NumbersUSA, the America First Policy Institute, and the Center for Renewing America — placing it squarely within the administration's broader immigration agenda.

The proposal goes further than the piecemeal restrictions that have dominated the immigration debate this year. Rather than tightening H-1B rules, raising wage floors, or adjusting per-country caps, it would redesign the entire legal immigration architecture for employment and family categories.

## How the Points System Would Work

Under the bill, prospective immigrants would accumulate points across several categories. A doctoral degree earns the highest education score, followed by master's and bachelor's degrees from accredited institutions. English language proficiency — demonstrated through standardised testing — adds points. A job offer with a salary above a specified threshold earns additional credit, as does falling within a preferred age range.

The system is modelled loosely on frameworks used by Canada and Australia, though with important differences. Canada's Express Entry system, for instance, awards points for Canadian work experience and provincial nominations — features that have no analogue in the Moore bill. The American version appears to weight salary and employer sponsorship more heavily, reflecting a philosophy that immigration should be tethered directly to demonstrated labour market value.

Critically, the bill would require employers to prove they attempted to recruit American workers before any foreign worker could be sponsored. This domestic recruitment mandate goes beyond the current PERM labour certification process, which immigration attorneys have long criticised as a rubber-stamp exercise but which at least provides a defined, if imperfect, pathway.

## Family and Diversity Categories

The bill eliminates the diversity visa lottery, which currently distributes 55,000 green cards annually to nationals of countries with historically low immigration to the United States. Indian nationals are not eligible for the diversity lottery — India is excluded as a high-admission country — but the elimination signals the bill's broader posture toward reducing overall immigration numbers.

Family-based immigration, currently the largest category of legal immigration, would be narrowed to spouses and minor children of U.S. citizens. The existing categories for adult children, siblings, and parents of citizens — which account for hundreds of thousands of green cards annually — would be eliminated. For Indian families, the sibling and parent categories have carried backlogs stretching 20 years or more, but they have remained a pathway, however slow. This bill would close it entirely.

## What It Means for Indian Professionals

The Indian professional community's relationship with the employment-based green card system is defined by one word: backlog. Indian-born applicants in the EB-2 category currently face estimated wait times exceeding 40 years. The EB-3 skilled worker category is similarly frozen. A points-based system could, in theory, break this logjam by removing per-country caps and selecting immigrants purely on merit criteria.

But the details matter enormously. If the points system imposes an overall numerical cap similar to or lower than the current 140,000 employment-based green cards per year, Indian applicants could find themselves competing against the entire world for the same limited slots — without the EB-1A self-petition or NIW escape routes that currently exist outside the employer-sponsored track.

> **"A points system without higher numbers is just a different way of saying no."**

The bill's requirement for demonstrated domestic recruitment adds another variable. Indian professionals on H-1B visas, many of whom are already employed by their sponsoring companies, would need their employers to conduct and document a genuine search for American workers before proceeding — a process that could add months or years to an already protracted timeline.

## Political Prospects

The Americans First Immigration Act has the backing of organisations that carry weight within the Republican caucus, but it faces structural obstacles. Comprehensive immigration reform bills have a well-documented history of dying in committee. The current Congress, narrowly divided, has shown little appetite for sweeping legislation on any front, and immigration bills that restructure legal pathways — as opposed to enforcement-focused measures — have even less traction.

The bill is more significant as a policy marker than as imminent legislation. It signals where the restrictionist wing of the party wants to take the conversation: away from adjustments to the existing system and toward its wholesale replacement. For Indian professionals currently navigating H-1B renewals, PERM filings, and EB-2 priority dates, the immediate reality remains the system in place — but the direction of the debate has shifted unmistakably.""",
    },
]

# ── Insert ────────────────────────────────────────────────────────
def insert_article(article):
    """Insert one article via curl (proxy-safe)."""
    now = datetime.now(timezone.utc).isoformat()
    article['created_at'] = now
    article['updated_at'] = now
    # Word count
    body_text = article.get('body', '')
    article['word_count'] = len(body_text.split())

    payload = json.dumps(article)
    result = subprocess.run(
        [
            'curl', '-s', '-X', 'POST',
            f'{SUPABASE_URL}/rest/v1/p2_articles',
            '-H', f'apikey: {SUPABASE_KEY}',
            '-H', f'Authorization: Bearer {SUPABASE_KEY}',
            '-H', 'Content-Type: application/json',
            '-H', 'Prefer: return=representation',
            '-d', payload,
        ],
        capture_output=True, text=True
    )
    return result.stdout, result.stderr

# ── Main ──────────────────────────────────────────────────────────
if __name__ == '__main__':
    for i, article in enumerate(ARTICLES, 1):
        print(f'\n{"="*60}')
        print(f'Article {i}: {article["headline"][:80]}')
        print(f'Slug: {article["slug"]}')
        print(f'Words: ~{len(article["body"].split())}')
        print(f'{"="*60}')

        stdout, stderr = insert_article(article)
        if stderr:
            print(f'STDERR: {stderr}')

        try:
            resp = json.loads(stdout)
            if isinstance(resp, list) and resp:
                rec = resp[0]
                print(f'✅ Inserted — id={rec.get("id")}, status={rec.get("status")}, slug={rec.get("slug")}')
            elif isinstance(resp, dict) and 'code' in resp:
                print(f'❌ Error: {resp.get("message", resp)}')
            else:
                print(f'Response: {stdout[:300]}')
        except json.JSONDecodeError:
            print(f'Raw response: {stdout[:300]}')

    print('\nDone.')
