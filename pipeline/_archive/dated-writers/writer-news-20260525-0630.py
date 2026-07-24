#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 06:30 UTC batch
Topics: 1) USCIS green card adjustment of status killed — PM-602-0199, consular processing required, EB-2 retrogressed, Vembu "come home"
        2) Rubio's 4-day India visit — Modi meeting, Quad, Jaishankar presser, defense, energy, trade, visa friction, anti-India racism
"""

import json, os, uuid, re, requests, subprocess
from datetime import datetime, timezone, timedelta
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

def sb_post(table, data):
    r = requests.post(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_get(table, params):
    r = requests.get(f"{SB_URL}/rest/v1/{table}", headers=HEADERS, params=params, timeout=30)
    r.raise_for_status()
    return r.json()

def sb_patch(table, params, data):
    h = {**HEADERS, "Prefer": "return=representation"}
    r = requests.patch(f"{SB_URL}/rest/v1/{table}", headers=h, params=params, json=data, timeout=30)
    r.raise_for_status()
    return r.json()

def make_slug(slug_base, date_suffix="20260525"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Duplicate check ──
existing = sb_get("p2_articles", {
    "select": "headline,slug",
    "status": "eq.published",
    "published_at": "gte.2026-05-23T00:00:00Z",
    "order": "published_at.desc",
    "limit": "80"
})
existing_slugs = {a["slug"] for a in existing}
existing_headlines_lower = {a["headline"].lower()[:60] for a in existing}
print(f"Found {len(existing)} recent articles for dedup check")

now = datetime.now(timezone.utc)
now_iso = now.isoformat().replace('+00:00', 'Z')
now_plus1 = (now + timedelta(minutes=1)).isoformat().replace('+00:00', 'Z')

articles = []

# ══════════════════════════════════════════════════════════════
# ARTICLE 1: USCIS Kills Adjustment of Status — Green Card Applicants Must Leave the US
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("uscis-green-card-adjustment-status-consular-processing-india-h1b-vembu")
headline1_prefix = "the us government just told"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Government Just Told Every Indian on an H-1B That if They Want a Green Card, They Must Leave the Country to Apply. The EB-2 India Wait Just Got Ten Months Longer.",
        "subheadline": "On May 22, USCIS released Policy Memorandum PM-602-0199, declaring adjustment of status — the process that let immigrants apply for a green card without leaving America — an 'extraordinary act of administrative grace' that will now be granted only in exceptional circumstances. Most applicants must return to their home country and process through a US consulate. The same week, the June 2026 Visa Bulletin retrogressed EB-2 India by 10.4 months to September 2013 and EB-1 India by 3.5 months. Immigration attorneys warn that leaving the US for consular processing risks triggering 3-year or 10-year reentry bars. Zoho founder Sridhar Vembu posted on X: 'Please come home. Even if you feel it is hardship and sacrifice, self-respect should dictate your course.' For the 283,000 Indians holding H-1B visas and the hundreds of thousands more in EB queues that already stretch past a decade, the path to permanent residence in America just narrowed to a point that may no longer be walkable.",
        "slug": slug1,
        "category": "news",
        "vertical": "immigration",
        "diaspora_angle": "This is not a policy change happening to someone else. If you are an Indian on an H-1B visa in America right now — and 283,000 of you are — the US government just told you that the green card process you have been waiting in, some of you for 10 or 15 years, no longer works the way you planned. Adjustment of status, the mechanism that let you file your I-485 while continuing to live and work in the US, has been reclassified as an 'extraordinary act of administrative grace.' That is bureaucratic language for: the default answer is now no. You must go home to apply. Not home to visit. Home to sit in a consulate queue whose timeline nobody can predict. Home where your children's American schools do not exist. Home where the career you spent fifteen years building pauses, or ends. Immigration lawyers are already warning clients about the 3-year and 10-year bars — if you have accumulated even a few days of unlawful presence, perhaps through a processing delay you did not cause, leaving the US for consular processing can trigger an automatic ban on reentry. This is not theoretical. This is the exact mechanism that has separated families for years. And it landed in the same week that the EB-2 India date moved backward by ten months, to September 2013. If you filed your green card application in 2014, you just got pushed further from the front of a line you have been standing in for a decade. Sridhar Vembu, the founder of Zoho, said the quiet part loudly: come home. Build in India. Stop waiting for a country that keeps changing the rules. Whether you agree with him or not, the fact that a billionaire tech founder is publicly telling Indian engineers to abandon the American dream is a measure of how broken the system has become.",
        "tags": ["USCIS", "green card", "H-1B", "adjustment of status", "consular processing", "EB-2", "EB-1", "India", "immigration", "PM-602-0199", "Sridhar Vembu", "Zoho", "visa bulletin", "NRI", "brain drain"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "USCIS — Will Grant Adjustment of Status Only in Extraordinary Circumstances (Official Release)", "url": "https://www.uscis.gov/newsroom/news-releases/us-citizenship-and-immigration-services-will-grant-adjustment-of-status-only-in-extraordinary"},
            {"name": "VisaVerge — USCIS Limits Adjustment of Status: Zoho Founder Sridhar Vembu Urges Indian Visa Holders to Come Home", "url": "https://www.visaverge.com/news/zoho-founder-sridhar-vembu-urges-indian-visa-holders-to-come-home-after-green-card-rule-tightening/"},
            {"name": "WSJ — Trump Administration to Make Green Card Applicants File Overseas", "url": "https://www.wsj.com/politics/policy/trump-green-card-adjustment-of-status-2026"},
            {"name": "Reuters — USCIS tells foreigners seeking green cards: Return to your countries to apply", "url": "https://www.reuters.com/world/us/uscis-tells-foreigners-seeking-green-cards-return-your-countries-apply-2026-05-22/"},
            {"name": "Outlook Business — Trump Administration Ends US-Based Green Cards for Temporary Visa Holders", "url": "https://outlookbusiness.com/economy/trump-administration-ends-us-based-green-cards-for-temporary-visa-holders"},
            {"name": "Bloomberg Law — Trump Administration Narrows Path to Seek Green Cards Inside US", "url": "https://news.bloomberglaw.com/daily-labor-report/trump-administration-narrows-path-to-seek-green-cards-inside-us"}
        ]),
        "score_total": 88,
        "status": "published",
        "published_at": now_iso,
        "body": """On May 22, 2026, the United States Citizenship and Immigration Services released a six-page policy memorandum that effectively ended the way most immigrants in America get their green cards.

Policy Memorandum PM-602-0199 declares that adjustment of status — the decades-old process that allowed immigrants already living in the US to apply for permanent residency without leaving the country — is an "extraordinary act of administrative grace." Under the new policy, most applicants must return to their home country and complete the green card process through a US consulate abroad.

The memo did not change the law. It reinterpreted it. And for the hundreds of thousands of Indian professionals who have spent years — some more than a decade — in employment-based green card queues while living and working in America under H-1B visas, that reinterpretation may have just broken the entire framework their lives were built around.

## What Changed

Until this memo, adjustment of status was the standard path. You filed an I-485 application with USCIS, continued working under your existing visa, and waited for your priority date to become current. When it did, your green card was approved without you ever having to leave the country. Your employer kept you. Your children stayed in school. Your mortgage stayed current. Life continued while the bureaucracy slowly processed your case.

Under PM-602-0199, that process is now the exception, not the rule.

USCIS spokesman Zach Kahler said in the official release: "An alien who is in the U.S. temporarily and wants a Green Card must return to their home country to apply, except in extraordinary circumstances. This policy allows our immigration system to function as the law intended instead of incentivizing loopholes."

The memo directs adjudicating officers to treat adjustment of status as discretionary relief that requires affirmative justification. Even applicants who meet every formal legal requirement can be denied on discretionary grounds. Officers are instructed to weigh conduct "inconsistent with the purpose of the visa" — a phrase so vague that immigration lawyers say it gives individual officers enormous subjective power over outcomes.

After immediate backlash, USCIS clarified on May 23 that exceptions would be considered for applications that provide an "economic benefit or otherwise are in the national interest." But the policy language does not define either standard, leaving applicants to guess whether their case qualifies.

## The Visa Bulletin Made It Worse

The timing was brutal.

The same week that USCIS announced the adjustment of status restrictions, the State Department published the June 2026 Visa Bulletin. For Indian applicants, the numbers moved in the wrong direction.

EB-2 India — the category that covers most Indian tech professionals with advanced degrees — retrogressed by 10.4 months, moving its final action date backward to September 1, 2013. If you are an Indian engineer who filed your green card application in 2014 or later, your priority date just moved further from the front of the line.

EB-1 India, the category for persons of extraordinary ability and multinational managers, retrogressed by 3.5 months to December 15, 2022.

EB-3 India offered a small consolation, advancing by one month to December 15, 2013. But EB-3 is the lower-preference category, and the movement was marginal.

The convergence of these two events — adjustment of status reclassified as extraordinary relief, and the visa bulletin moving backward — creates a double squeeze. The domestic path is harder to access. The overseas path requires leaving the country. And the timeline for either path just got longer.

## The 3-Year and 10-Year Bars

Immigration attorneys immediately flagged the most dangerous hidden risk in the new policy: the unlawful presence bars.

Under existing US immigration law, a person who accumulates more than 180 days of unlawful presence in the US and then departs is automatically barred from reentry for three years. If the unlawful presence exceeds one year, the bar extends to ten years.

The catch is that unlawful presence can accumulate through no fault of the applicant. Processing delays, employer errors in filing extensions, gaps between visa categories — any of these can create days or weeks of technical unlawful presence that the applicant may not even know about.

When adjustment of status was the default, this risk was largely contained. You stayed in the country. You did not trigger the departure that activates the bar. Under the new policy, if you must leave for consular processing, any accumulated unlawful presence becomes a live grenade.

An immigration lawyer quoted by Bloomberg Law described the scenario: "You leave the US to attend your consular interview. At the interview, they discover 200 days of unlawful presence from a gap three years ago. You are now subject to a three-year bar. You cannot return. Your job is gone. Your family is split."

This is not an edge case. For Indian professionals who have been in the US for 10 to 15 years, cycling through H-1B renewals, employer changes, and status transfers, the odds of having accumulated some period of technical unlawful presence are significant.

## The Numbers

Indians dominate the US employment-based immigration system in a way no other nationality does.

Of the 406,348 H-1B petitions approved in the most recent fiscal year, 283,772 — roughly 70 percent — went to Indian nationals. The next largest group, Chinese nationals, accounted for approximately 12 percent. No other country comes close.

The EB-2 and EB-3 backlogs for India are measured not in months but in decades. An Indian national who filed an EB-2 petition today would wait an estimated 30 to 50 years for a green card under current per-country limits — limits that cap India at the same 7 percent of employment-based green cards as countries with a fraction of the demand.

The adjustment of status process was the mechanism that made this wait survivable. You could work. You could get promoted. You could buy a house. Your children could grow up American in every way except on paper. The new policy does not change the wait time. It changes whether you can wait in America.

## Sridhar Vembu Says Come Home

On May 23, one day after the USCIS announcement, Zoho founder Sridhar Vembu posted on X: "Once again, my appeal to Indians in America on a visa. Please come home. Even if you feel it is hardship and sacrifice, self-respect should dictate your course. Let's make Bharat proud."

Vembu is not a random commentator. He is the founder and CEO of Zoho Corporation, a privately held software company with $1 billion in annual revenue, 15,000 employees, and a deliberate strategy of building in India rather than Silicon Valley. He relocated from the Bay Area to a village in Tamil Nadu in 2020 and has been vocal about reverse brain drain ever since.

His argument is straightforward: India's technology ecosystem has matured to the point where talented engineers no longer need to tolerate a hostile immigration system abroad. Zoho, Flipkart, Razorpay, Zerodha, PhonePe — the examples of Indian companies building world-class products from Indian cities are now numerous enough that the "you have to be in America to matter" assumption no longer holds.

Whether Indian professionals agree with Vembu or not, the fact that a billionaire tech founder is publicly advising Indians to abandon the American dream is itself a data point about how broken the system has become.

## What Rubio Said in India

The USCIS memo was released on the same day that US Secretary of State Marco Rubio arrived in India for a four-day visit. At a joint press conference with External Affairs Minister S. Jaishankar on May 24, Rubio was asked directly about the visa changes.

His response was careful but telling: "The changes that are happening now, or the modernisation of our migration system into the United States, are not India-specific. It is global, it's being applied across the world. We are in a period of modernisation."

He acknowledged that the reforms would create "friction points" during the transition period but insisted the US remained "the most welcoming country in the world on immigration."

Jaishankar did not publicly press the issue, but Indian media reported that visa concerns were raised in the bilateral discussions. The diplomatic reality is clear: India cannot afford to make immigration the centerpiece of a relationship that also involves defense contracts, energy deals, and a shared interest in containing China. The 283,000 Indians on H-1B visas are, in the language of diplomacy, a friction point — not a dealbreaker.

## What Happens Now

The legal landscape is already shifting. Immigration law firms are advising clients to take immediate steps:

**Review your entire immigration history** for any periods of potential unlawful presence. If you have gaps, consult an attorney before making any travel plans.

**File any pending I-485 applications immediately** if your priority date is current. The memo applies prospectively to new adjudications, and applications already in the pipeline may receive different treatment — though this is not guaranteed.

**Consider the I-140 portability provisions** carefully. If you change employers, your I-140 approval may follow you, but the interaction with the new consular processing requirements adds complexity.

**Do not leave the United States** for any reason until you understand how the new policy interacts with your specific case. A routine trip to India to visit family could become the trigger for a 3-year or 10-year bar if your immigration history contains any unlawful presence.

Several immigration advocacy groups have announced plans to challenge the memo in federal court, arguing that USCIS is exceeding its authority by reinterpreting a statutory right as discretionary relief. But litigation takes time, and the memo is effective immediately.

## The Fundamental Question

For the Indian professional who came to America on an H-1B visa ten years ago, who has paid taxes, bought a home, raised American-born children, contributed to the companies that drive the American economy, and waited patiently in a green card line that moves at geological speed — the fundamental question has changed.

It used to be: how long will I wait?

Now it is: can I wait here?

The US government's answer, as of May 22, 2026, is: probably not. Go home and apply from there. And if you have accumulated even a few days of unlawful presence during the decade you spent following every rule, leaving might mean you cannot come back.

Sridhar Vembu's answer is different but equally stark: stop waiting. Come home to India. Build something there.

Neither answer is easy. But for the first time in the history of the Indian diaspora in America, the question of whether to stay or leave is no longer theoretical. The US government just made it structural."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Rubio's Four-Day India Visit — Defense, Energy, Trade, and the Quad
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("rubio-india-modi-jaishankar-quad-defense-energy-trade-tariffs-iran")
headline2_prefix = "marco rubio just spent four days"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Marco Rubio Just Spent Four Days in India. He Brought a White House Invitation, a Defense Deal Renewal, an Energy Pitch, and No Trade Agreement. Here Is What It Means for the Diaspora.",
        "subheadline": "The US Secretary of State arrived in Kolkata on May 23 — the first such visit to the city in fourteen years — and worked his way through Agra, Jaipur, and New Delhi in a trip designed to signal strategic depth at a time when tariffs, the Iran war, and Washington's warming ties with Pakistan have strained the relationship. He met Modi, renewed a 10-year defense framework, signed an underwater domain awareness roadmap, pushed American energy exports as India's route off Russian oil, acknowledged that immigration reforms are creating 'friction points' for Indians, and called anti-India racist comments the work of 'stupid people.' On Monday, the Quad foreign ministers meet in New Delhi. The trade deal that was supposed to follow the February interim framework is still not done. For 4.4 million Indian Americans watching this visit, the signals are mixed: America wants India as a strategic partner but keeps raising the price of the relationship.",
        "slug": slug2,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "If you are an Indian American, this visit was about you — even though your name never came up. When Rubio tells Modi that US energy can diversify India's supply, he is talking about whether your parents' cooking gas gets cheaper. When Jaishankar pushes 'Make in India' for defense, he is talking about the factory jobs that keep your cousin in Pune instead of driving a cab in New Jersey. When Rubio says immigration reforms create 'friction points,' he is talking about your H-1B renewal. When he calls anti-Indian racism the work of 'stupid people,' he is talking about the comments your friend got at a gas station in Texas. The Quad meeting on Monday is about whether China controls the shipping lanes your family's goods travel on. The trade deal that still is not signed is about whether the mangoes, textiles, and IT services that connect India to America flow freely or through a tariff wall. Every piece of this four-day visit touches the diaspora. The question is whether it touches you as a strategic asset or a friction point.",
        "tags": ["Rubio", "India", "Modi", "Jaishankar", "Quad", "defense", "energy", "trade", "tariffs", "Iran", "Pakistan", "Indo-Pacific", "NRI", "H-1B", "racism", "diplomacy", "Sergio Gor"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Foreign Policy Journal — Marco Rubio Arrives in India for Quad Meeting as US Scrambles to Repair Tariff-Damaged Relations", "url": "https://www.foreignpolicyjournal.com/2026/05/24/marco-rubio-arrives-in-india-for-quad-meeting-as-us-scrambles-to-repair-tariff-damaged-relations/"},
            {"name": "CurrentIndia / Times of India — From Anti-India Racism to Visa Issues: Key Takeaways from Rubio-Jaishankar Joint Press Conference", "url": "https://currentindia.com/channels/timesofindia/toi-india/from-anti-india-racism-to-visa-issues-key-takeaways-from-rubio-jaishankar-joint-press-conference/"},
            {"name": "MetaPress / AFP — Rubio Touts US Energy on India Trip Meant to Repair Ties", "url": "https://metapress.net/asia/2026/05/24/rubio-touts-us-energy-on-india-trip-meant-to-repair-ties/"},
            {"name": "DefenceStar.in — Marco Rubio Meets Modi in New Delhi, Reviews Strategic Cooperation", "url": "https://defencestar.in/marco-rubio-meets-modi-in-new-delhi/"},
            {"name": "Pune Prime / Times of India — EAM Jaishankar Pushes 'Make in India' Approach in Talks with Marco Rubio", "url": "https://puneprime.news/indo-us-defence-ties-eam-jaishankar-pushes-make-in-india-approach-in-talks-with-marco-rubio-the-times-of-india/"},
            {"name": "CSIS (Richard Rossow) — Lack of Trade Agreement Clouds Engagement", "url": "https://www.csis.org/"},
            {"name": "Jaishankar Outlines India's 5-Point Stand During Talks with Rubio", "url": "https://www.dailyworld.in/article/dialogue-uninterrupted-maritime-trade-eam-jaishankar-outlines-indias-5-point-stand-during-talks-with-rubio/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_plus1,
        "body": """When the US Secretary of State flies to another country for four days, it is not a social call. When that country is India, and the visit includes the cities of Kolkata, Agra, Jaipur, and New Delhi in rapid succession, every stop is a message.

Marco Rubio arrived in Kolkata on May 23, 2026 — the first US Secretary of State to visit the city in nearly fourteen years. His first stop was the Missionaries of Charity headquarters, the organisation founded by Mother Teresa. The symbolism was deliberate: shared values, a moral foundation, a relationship deeper than transactional. US Ambassador Sergio Gor, who accompanied Rubio throughout, called it a reflection of the partnership "beyond pure policy transactions."

From Kolkata, Rubio flew to New Delhi to meet Prime Minister Narendra Modi. Then came Agra and Jaipur — cultural stops that diplomats call "optics" and analysts call "signaling strategic depth." Then back to New Delhi for the main event: delegation-level talks with External Affairs Minister S. Jaishankar, followed by a joint press conference at Hyderabad House, and on Monday, May 26, the Quad Foreign Ministers' Meeting that brings together the US, India, Japan, and Australia.

The agenda was enormous. The results were mixed.

## The Defense Renewal

The most concrete outcome of the visit was the renewal of the 10-year US-India Major Defence Partnership Framework Agreement, originally signed in October last year.

Jaishankar announced at the press conference that both sides had also signed a comprehensive underwater domain awareness roadmap — a technical agreement that covers submarine detection, maritime surveillance, and the kind of deep-ocean intelligence sharing that matters enormously in the Indo-Pacific, where Chinese submarines are an increasing concern.

"We discussed the importance of taking into account the Make in India approach and lessons drawn from recent conflicts while going forward in the defence domain," Jaishankar said. The "Make in India" reference was pointed: India wants American defense technology manufactured on Indian soil, not just sold as finished products. Co-production, not procurement.

The defense relationship is the strongest pillar of the US-India partnership, and the renewal signals that both governments want it to remain so regardless of tensions in other areas.

## The Energy Pitch

Rubio came to India selling energy. He told Modi that "US energy products have the potential to diversify India's energy supply" and "emphasised that the United States will not let Iran hold the global energy market hostage."

The subtext is enormous. India imports 85 percent of its crude oil. Before the Iran war erupted in February 2026, roughly 45 percent of those imports transited the Strait of Hormuz, which was closed for three months. India has been buying heavily from Russia — $46 billion in crude in the current fiscal year — to fill the gap. The US has long wanted India to reduce its Russian oil dependency, and the Iran war's disruption of the energy market gave Washington a new argument: buy from us instead.

Jaishankar's response was diplomatic but firm: "A big country, if you want to de-risk, looks at multiple sourcing. For us, the United States has emerged as a very significant and reliable source." He added that India would "continue to diversify and maintain multiple sources of supply at the most reasonable cost."

Translation: India will buy American energy when the price is right, but will not abandon Russian or Gulf suppliers to please Washington. India's 1.4 billion people need affordable fuel, and energy policy is driven by economics, not alliance loyalty.

Both sides also discussed nuclear energy cooperation following the passage of the Shanti Act, which Jaishankar said had opened "new possibilities" in the nuclear domain. He flagged unresolved regulatory issues on the American side — a quiet acknowledgment that bureaucratic obstacles in Washington are slowing what could be a major area of collaboration.

## The Trade Deal That Still Isn't Done

In February 2026, after Trump's tariffs hit Indian goods at a punishing 50 percent, the two countries negotiated an interim framework that reduced the rate to 18 percent. It was announced with fanfare. It was supposed to be the first step toward a comprehensive bilateral trade agreement envisioned during Modi's US visit in February 2025.

Three months later, the deal is still not finalised.

Part of the delay is structural: in late February, the US Supreme Court struck down Trump's reciprocal tariffs, effectively bringing the duty rate on Indian goods down to about 10 percent. That removed the immediate pressure on India to sign an agreement. New Delhi has been weighing its options, aware that the Trump administration is pursuing trade investigations under unfair practices legislation that could restore higher levies.

Rubio was asked directly whether the relationship had lost momentum. His answer was emphatic: "The US-India relationship has not lost any momentum. I understand why some people might say that, but I don't see it or view that in any way, shape, or form."

He said an Indian trade delegation had recently visited Washington and a US team was expected in India soon. "We are hopeful that we will wind up with a trade agreement that is going to be enduring, beneficial to both sides, and sustainable."

Jaishankar said both sides were pushing for "an early conclusion" of the interim text.

Not everyone is optimistic. Richard Rossow of the Center for Strategic and International Studies said the "lack of a trade agreement — more than three months after the announcement of the 'interim deal' — clouds other areas of engagement." He described the Quad meeting — the third without a leader-level engagement — as "an unannounced downgrade" of the grouping.

The trade deal matters enormously to the diaspora. Indian IT services, textiles, pharmaceuticals, agriculture — the sectors that employ millions in India and connect the two economies — all sit behind tariff walls that have not been resolved. Every month without a deal is a month of uncertainty for the businesses that sustain families on both sides.

## The Iran Factor

Rubio used the India press conference to hint at progress on the Iran conflict.

"The president's preference is to find a diplomatic way. He would much rather have me in the State Department solve this problem than the Department of War having to solve it. But the problem's gonna be solved one way or the other," Rubio said.

He suggested there could be "good news in the next few hours" on the Strait of Hormuz, but cautioned: "You can agree to things on paper. They actually have to be implemented. I do think there is some good news on that front, but not final news on that front."

On nuclear weapons: "They will never possess a nuclear weapon, certainly not as long as Donald Trump is president of the United States."

Modi, for his part, did not mention Iran by name. He reiterated India's support for "peaceful resolution of conflict through dialogue and diplomacy."

The Iran dimension matters to India because of energy and to the diaspora because of the economic cascade: crude prices drive the rupee, the rupee drives inflation, inflation drives the cost of everything your family in India buys. If Rubio's "good news" materialises — if the Strait of Hormuz reopens and crude drops — the relief would be immediate. If it does not, the current trajectory of ₹95+ rupee, ₹113 petrol, and record electricity bills continues.

## The Pakistan Irritant

Asked about Washington's growing engagement with Pakistan — which has emerged as a key interlocutor in the Iran negotiations — Rubio gave a carefully worded response: "I don't view our relation with any country in the world as coming at the expense of our strategic alliance with India."

The word "alliance" was notably stronger than the typical diplomatic vocabulary of "partnership." Whether it reflects a genuine upgrade in how the US views India or simply Rubio's attempt to soothe anxieties in the room is a matter of interpretation.

For India, the US-Pakistan dynamic is a perpetual sore point. When Washington courts Islamabad — for Afghanistan access, for Iran mediation, for counterterrorism cooperation — New Delhi reads it as a signal that its own strategic value is conditional. Rubio's assurance was meant to counter that reading.

Jaishankar positioned India above the fray: "India is one of the very few countries with strong ties to the US, Israel, Iran and Gulf nations simultaneously. We don't look at it as a zero-sum game."

## The Visa Question and Anti-India Racism

In the most personally resonant moment of the press conference, Rubio was asked about changes to J-1, F-1, and H-1B visa policies and about racist comments targeting Indian Americans.

On visas, he said the reforms were "not India-specific" and were part of a global modernisation of the US immigration system. He acknowledged India's economic contribution — "$20 billion invested in the US economy by Indian companies" — and said the US wanted that number to continue increasing. But he admitted the reforms would create "friction points."

On racism: "I'll take that very seriously about the comments. I'm sure that there are people who have made comments online and in other places because every country in the world has stupid people."

He pivoted to the positive: "The United States is a very welcoming country. Our nation has been enriched by people who come to our country from all over the world." He noted that his own parents migrated from Cuba in 1956.

The response was diplomatically adequate but practically limited. For the Indian American who has been told to "go back to your country" at a grocery store in Ohio, or the H-1B holder whose USCIS case was just reclassified as "extraordinary circumstances only," the Secretary of State calling racists "stupid people" does not change the lived experience. But the fact that the question was asked at a joint press conference — and that Rubio answered it publicly — reflects how central these issues have become to the US-India relationship.

## The Quad on Monday

The centrepiece of the visit is Monday's Quad Foreign Ministers' Meeting at Hyderabad House. The meeting is expected to produce a joint statement covering freedom of navigation in the South China Sea, cybersecurity cooperation, critical mineral supply chain resilience, and coordination on the humanitarian and economic consequences of the Iran war.

Rubio called the Quad "a form of alignment between four countries who are not just strategically aligned, but four countries that have the ability to influence global events on these topics of mutual interest."

Jaishankar framed it in terms of identity: "We are doing a lot with each other because we are maritime powers, and because we are democratic powers. For us, particularly in the Indo Pacific, it's very important that the core cooperation as maritime democracies continue."

The Quad matters to the diaspora because it is the institutional framework through which India participates in the rules-based order that governs the seas your goods travel on, the supply chains your companies depend on, and the security architecture that prevents the kind of conflict that would make all other questions — trade, visas, energy — irrelevant.

## What This Visit Means

Here is the honest assessment: Rubio's visit was important, productive, and incomplete.

**Important** because the US Secretary of State spent four days in India at a moment when the relationship needed visible attention. The defense renewal is real. The energy discussions are real. The Quad is real. The White House invitation to Modi — extended by Rubio on Trump's behalf — is a signal that the relationship has not been downgraded, regardless of what tariffs and immigration policies might suggest.

**Productive** because the two governments found enough common ground to keep the strategic partnership moving forward on defense, technology, and Indo-Pacific coordination. Jaishankar's 5-point stand — dialogue, uninterrupted maritime trade, opposition to trade weaponisation, adherence to international law, and resilient supply chains — was a confident articulation of India's position in a multi-polar world.

**Incomplete** because the trade deal that would resolve the tariff uncertainty is still not done. Because the immigration reforms that are reshaping the lives of hundreds of thousands of Indian professionals were acknowledged as "friction points" but not addressed. Because the Iran conflict that is driving India's energy crisis and the rupee's collapse received hints of progress but no resolution. Because Trump still has not visited India, and the Quad still has not had a leader-level meeting.

For 4.4 million Indian Americans, the visit is a reminder that the US-India relationship is enormous, consequential, and perpetually unfinished. America wants India as a strategic partner. It wants Indian engineers, Indian investment, Indian cooperation on China. But it also wants to sell India energy at American prices, restrict Indian immigration at American discretion, and negotiate trade deals on American timelines.

The diaspora lives in the space between those wants. Rubio's visit did not resolve that tension. It made it visible."""
    })
    print(f"✅ Article 2 queued: {slug2}")
else:
    print(f"⏭️  Article 2 skipped (duplicate): {slug2}")


# ── Insert articles ──
for article in articles:
    try:
        result = sb_post("p2_articles", article)
        print(f"✅ Inserted: {article['slug']} → {article['id']}")
    except Exception as e:
        print(f"❌ Insert failed for {article['slug']}: {e}")

print(f"\n{'='*60}")
print(f"Published {len(articles)} articles")
print(f"{'='*60}")

# ── Source images for articles ──
PEXELS_KEY = ""
pexels_env = Path.home() / "workspace" / ".env.pexels"
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if "=" in line and not line.startswith("#"):
            k, v = line.split("=", 1)
            if "pexels" in k.lower():
                PEXELS_KEY = v.strip()

def search_pexels(query, per_page=5):
    if not PEXELS_KEY:
        return []
    r = requests.get(
        "https://api.pexels.com/v1/search",
        headers={"Authorization": PEXELS_KEY},
        params={"query": query, "per_page": per_page, "orientation": "landscape"},
        timeout=15,
    )
    if r.status_code == 200:
        return r.json().get("photos", [])
    return []

def get_pexels_image_url(query):
    photos = search_pexels(query)
    if photos:
        return photos[0]["src"]["large2x"]
    return None

image_queries = {
    slug1: "US visa passport immigration documents green card",
    slug2: "India flag diplomatic meeting government officials",
}

for art in articles:
    slug = art["slug"]
    query = image_queries.get(slug, "")
    if not query:
        continue
    img_url = get_pexels_image_url(query)
    if img_url:
        try:
            sb_patch("p2_articles", {"id": f"eq.{art['id']}"}, {"image_url": img_url})
            print(f"🖼️  Image set for {slug}: {img_url[:80]}...")
        except Exception as e:
            print(f"⚠️  Image PATCH failed for {slug}: {e}")
    else:
        print(f"⚠️  No Pexels image found for {slug}")

# ── Score decay for news articles older than 12h ──
try:
    decay_articles = sb_get("p2_articles", {
        "select": "id,score_total,published_at",
        "status": "eq.published",
        "category": "eq.news",
        "score_total": "gt.40",
        "published_at": "lt." + (now - timedelta(hours=12)).isoformat().replace('+00:00', 'Z'),
        "order": "published_at.desc",
        "limit": "50"
    })
    decayed = 0
    for a in decay_articles:
        age_hours = (now - datetime.fromisoformat(a["published_at"].replace('Z', '+00:00'))).total_seconds() / 3600
        if age_hours > 48:
            decay = 3
        elif age_hours > 24:
            decay = 2
        else:
            decay = 1
        new_score = max(40, a["score_total"] - decay)
        if new_score != a["score_total"]:
            sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": new_score})
            decayed += 1
    print(f"\n📉 Score decay: {decayed} news articles decayed")
except Exception as e:
    print(f"⚠️ Score decay error: {e}")

# ── Git commit & push ──
try:
    repo = Path.home() / "workspace" / "the-videshi-news"
    subprocess.run(["git", "add", "-A"], cwd=repo, capture_output=True, timeout=30)
    msg = f"news: USCIS green card policy + Rubio India visit ({now.strftime('%Y-%m-%d %H:%M UTC')})"
    subprocess.run(["git", "commit", "-m", msg, "--allow-empty"], cwd=repo, capture_output=True, timeout=30)
    push = subprocess.run(["git", "push"], cwd=repo, capture_output=True, timeout=60)
    if push.returncode == 0:
        print("🚀 Git push successful → Vercel deploy triggered")
    else:
        print(f"⚠️ Git push issue: {push.stderr.decode()[:200]}")
except Exception as e:
    print(f"⚠️ Git error: {e}")

print("\n✅ Writer pipeline complete")
