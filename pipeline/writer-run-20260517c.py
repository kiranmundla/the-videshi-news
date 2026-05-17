#!/usr/bin/env python3
"""Videshi Writer — NEWS run 2026-05-17 batch C (post-22:57 UTC)"""

import json, os, sys, uuid, subprocess, urllib.request, urllib.parse, time, re, hashlib
from datetime import datetime, timezone

# --- Supabase credentials ---
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", os.environ.get("SUPABASE_ANON_KEY", ""))
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def sb_request(method, path, data=None, extra_headers=None, retries=3):
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    body = json.dumps(data).encode() if data else None
    h = dict(HEADERS)
    if extra_headers:
        h.update(extra_headers)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, data=body, headers=h, method=method)
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode())
        except urllib.error.HTTPError as e:
            err = e.read().decode()
            print(f"  ERROR {e.code}: {err[:300]}")
            return None
        except Exception as e:
            if attempt < retries - 1:
                print(f"  Retry {attempt+1}/{retries}: {type(e).__name__}")
                time.sleep(2 * (attempt + 1))
            else:
                print(f"  FAILED after {retries} attempts: {e}")
                return None

def sb_get(path):
    return sb_request("GET", path)

def sb_post(path, data):
    return sb_request("POST", path, data)

def sb_patch(path, data):
    return sb_request("PATCH", path, data, {"Prefer": "return=representation"})

now_iso = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: BHOJSHALA VERDICT (news)
# ============================================================
art1_id = str(uuid.uuid4())
art1_slug = "bhojshala-verdict-mp-high-court-temple-saraswati-20260517"
art1 = {
    "id": art1_id,
    "headline": "A 900-Year-Old Building, a Goddess in London, and the Court Verdict That Just Rewrote Dhar's Future",
    "subheadline": "The Madhya Pradesh High Court has declared the Bhojshala complex a Hindu temple dedicated to Goddess Saraswati — quashing two decades of shared worship and ordering the repatriation of a medieval idol from the British Museum.",
    "body": """The Madhya Pradesh High Court has ended a dispute that has simmered since at least the 1930s. In a sweeping verdict running to 242 pages, the court declared the Bhojshala–Kamal Maula complex in Dhar a Hindu temple, overturning a 2003 order by the Archaeological Survey of India that had permitted Muslim Friday prayers at the site alongside Hindu worship on Tuesdays.

## What the Court Said

The bench ruled that the complex — built in the eleventh century by the Paramara king Bhoja — was "predominantly and originally" a Hindu temple and Sanskrit academy dedicated to Goddess Vagdevi (Saraswati). The judgment drew on a 98-day ASI survey that documented inscriptions, architectural features, and iconographic evidence supporting a Hindu character predating any Islamic usage.

Crucially, the court held that the Places of Worship Act, 1991 — which generally freezes the religious character of monuments as of August 15, 1947 — does not apply here, because Bhojshala was designated a centrally protected monument as far back as 1904. That exemption had been the legal crux of the case.

The court also quashed the ASI's 2003 administrative order that had created a time-sharing arrangement between Hindu and Muslim worshippers, calling it an executive action that had no statutory basis.

## The Idol in London

Perhaps the most dramatic directive involves a medieval stone idol of Goddess Saraswati (Vagdevi) that was removed from the Bhojshala complex in the colonial era and is currently held at the British Museum in London. The court has directed the central government to initiate diplomatic efforts for the idol's repatriation — a request that adds Bhojshala to the growing list of Indian heritage restitution cases that have gained traction in recent years.

For the Indian diaspora in the UK, the idol's status has been a quiet cause for decades. Community organisations in London have periodically petitioned for its return, arguing that it is not a museum artefact but a living object of devotion.

## The Fallout

The verdict was met with celebration by Hindu groups, including the Vishva Hindu Parishad, which called it a "cultural restoration." Union Minister Savitri Thakur, who represents the Dhar constituency, said the temple would now remain open for "uninterrupted Hindu worship."

The All India Muslim Personal Law Board (AIMPLB) has announced it will challenge the ruling in the Supreme Court, calling it a departure from the established constitutional position on heritage sites. The court's suggestion that alternative land be provided to Muslims for a mosque has done little to assuage these concerns.

Security in Dhar has been stepped up. The district administration imposed restrictions on gatherings and increased police deployments in the old city, where the complex sits.

## Why the Diaspora Is Watching

Bhojshala sits in a line of heritage dispute verdicts — after Ayodhya (2019) and the ongoing Gyanvapi case in Varanasi — that have reshaped the legal landscape around India's syncretic monuments. For NRIs, these cases are about more than property. They are about how India arbitrates competing claims to its civilisational past, and whether the Places of Worship Act will hold as a constitutional firewall.

The repatriation question, meanwhile, places Bhojshala in the same frame as the Kohinoor diamond and the Sultanganj Buddha — objects of cultural sovereignty that the diaspora views through a lens of colonial redress.

## What Happens Next

The AIMPLB's Supreme Court challenge could take months or years. In the interim, the ASI will manage the site under the court's new framework, with Hindu worship permitted daily. The repatriation request to the British Museum will test India's diplomatic muscle — and London's willingness to set new precedents on colonial-era acquisitions.

For now, the 900-year-old walls of Bhojshala will echo with only one kind of prayer. Whether that endures will depend on what the Supreme Court decides — and how many more of these verdicts are still to come.""",
    "diaspora_angle": "The idol repatriation directive places Bhojshala alongside Kohinoor and other colonial-era heritage claims NRIs have long championed. UK-based diaspora groups have petitioned for the Saraswati idol's return for decades.",
    "vertical": "politics",
    "tags": ["Bhojshala", "Madhya Pradesh High Court", "Goddess Saraswati", "Places of Worship Act", "British Museum", "ASI", "heritage dispute", "Dhar"],
    "urgency": "breaking",
    "sources": [
        {"url": "https://devdiscourse.com/article/headlines/bhojshala-temple-recognized-hindu-culture", "name": "Devdiscourse"},
        {"url": "https://en.wikipedia.org/wiki/Bhojshala", "name": "Wikipedia"},
        {"url": "https://legalserviceindia.com/bhojshala-temple-mosque-verdict", "name": "Legal Service India"},
        {"url": "https://latestly.com/india/bhojshala-dhar-madhya-pradesh-verdict", "name": "LatestLY"}
    ],
    "slug": art1_slug,
    "word_count": 720,
    "status": "published",
    "published_at": now_iso,
    "category": "news",
    "image_entities": ["Bhojshala complex", "Goddess Saraswati idol", "Dhar Madhya Pradesh"],
    "image_must_show": "Bhojshala temple complex or Saraswati idol",
    "image_search_query": "Bhojshala temple Dhar Madhya Pradesh",
    "score_total": 82
}

# ============================================================
# ARTICLE 2: CANADA KIDNAPPING (nri-world)
# ============================================================
art2_id = str(uuid.uuid4())
art2_slug = "indian-origin-men-arrested-canada-kidnapping-extortion-calgary-20260517"
art2 = {
    "id": art2_id,
    "headline": "Four Indian-Origin Men Arrested Across Three Provinces in a Kidnapping Scheme That Targeted Their Own Community",
    "subheadline": "Calgary police say the suspects — arrested in Brampton, Surrey, and Edmonton — lured one man to abduct another, in a case a detective called unlike anything he had seen before.",
    "body": """Canadian police have arrested four Indian-origin men in connection with a kidnapping and extortion scheme that targeted members of the South Asian community in Calgary. A fifth suspect remains at large.

## What Happened

On May 6, a man in Calgary was contacted by acquaintances and asked to come to a meeting point. When he arrived, he was grabbed, assaulted, and forced into a vehicle. The suspects threatened him with firearms and demanded money. He was released several hours later after being driven to a secondary location.

What made the case unusual, according to Calgary Police Service investigators, was its structure: the victim was not the original target. He was lured so that the suspects could use him to access and extort a third party. A detective working the case told Canadian media he had "never seen" a kidnapping structured in quite that way.

## The Arrests

The four suspects — all Indian-origin men in their twenties — were arrested over the following ten days across three Canadian provinces. Arrests were made in Brampton, Ontario; Surrey, British Columbia; and Edmonton, Alberta. All face charges including kidnapping, extortion, assault with a weapon, and firearms offences. A fifth suspect, identified as Gagandeep Singh, remains wanted.

The geographic spread of the arrests — spanning nearly 4,000 kilometres from British Columbia to Ontario — suggests a network rather than a localised crew. Police said the investigation involved coordination with RCMP detachments and municipal forces in multiple jurisdictions.

## A Pattern That Concerns the Community

The arrests come amid a broader wave of extortion-related violence targeting South Asian communities in Canada. Over the past two years, police forces in British Columbia, Ontario, and Alberta have documented a sharp increase in extortion cases — many involving threats delivered via social media, followed by arson, shootings at homes, and kidnapping.

In Brampton and Surrey, two cities with large Punjabi populations, community leaders have expressed frustration that law enforcement responses have been slow. Several high-profile cases have involved suspects with links to India, raising uncomfortable questions about whether criminal networks are operating across borders.

For the estimated 1.86 million people of Indian origin in Canada — the country's largest visible minority group — the cases are deeply unsettling. Community organisations have called for dedicated task forces and better engagement between police and South Asian residents, many of whom are reluctant to report threats.

## The Broader Context

Canada's relationship with its Indian diaspora has been fraught in recent years. The diplomatic fallout over the killing of Hardeep Singh Nijjar in Surrey in 2023, and subsequent allegations of Indian government involvement, reshaped bilateral relations and cast a shadow over the community. Extortion networks — whether linked to gangs in India, local criminal enterprises, or a mix — add another layer of insecurity.

The Calgary case also underscores how quickly extortion tactics have escalated. What once involved phone threats and demands for cryptocurrency has moved to physical kidnapping and firearms. Police say the suspects showed no regard for the risks of operating so openly.

## What Happens Next

The four arrested suspects are in custody and awaiting court appearances. Calgary police have asked anyone with information about the fifth suspect to come forward. Community leaders in Alberta have called for a public forum on extortion targeting South Asian Canadians.

For Indian-origin families across Canada, the case is a reminder that the diaspora's growing visibility and prosperity have also made it a target — and that the institutions meant to protect them are still catching up.""",
    "diaspora_angle": "Canada is home to 1.86 million Indian-origin people. Rising extortion and kidnapping targeting South Asian communities has become a defining safety concern for NRIs across the country.",
    "vertical": "diaspora",
    "tags": ["Canada", "Calgary police", "kidnapping", "extortion", "South Asian community", "Indian diaspora", "Brampton", "Surrey"],
    "urgency": "breaking",
    "sources": [
        {"url": "https://thenationalbulletin.in/canadian-police-arrest-four-indian-origin-kidnapping", "name": "The National Bulletin"},
        {"url": "https://aihustlehq.com/canadian-police-arrest-indian-kidnapping-extortion", "name": "AI Hustle HQ"},
        {"url": "https://healthandfitnesstoguide.com/4-indians-arrested-extortion-kidnapping-canada", "name": "HFG Insider"}
    ],
    "slug": art2_slug,
    "word_count": 680,
    "status": "published",
    "published_at": now_iso,
    "category": "nri-world",
    "image_entities": ["Calgary Police Service", "South Asian community Canada"],
    "image_must_show": "Calgary police or Canadian law enforcement",
    "image_search_query": "Calgary Police Service headquarters",
    "score_total": 80
}

# ============================================================
# ARTICLE 3: MARK STEVENS / NVIDIA MEDICAL SCHOOL (technology)
# ============================================================
art3_id = str(uuid.uuid4())
art3_slug = "nvidia-mark-stevens-175-million-medical-school-silicon-valley-20260517"
art3 = {
    "id": art3_id,
    "headline": "An Nvidia Billionaire Is Building Silicon Valley's First Medical School in a Century. Here's Why It Matters.",
    "subheadline": "Mark and Mary Stevens' $175 million gift will create a new medical school at Santa Clara University — the Bay Area's first in over 100 years — with AI and digital health baked into the curriculum from day one.",
    "body": """Mark Stevens, the billionaire venture capitalist who sits on Nvidia's board and co-owns the Golden State Warriors, has committed $175 million to build a medical school in the heart of Silicon Valley. The Mark & Mary Stevens School of Medicine, a joint venture between Santa Clara University and Sutter Health, will be the San Francisco Bay Area's first new medical school in over a century.

## What's Being Built

The school will occupy an 82,000-square-foot campus in Santa Clara, training 120 students per year once fully operational — roughly 30 to 40 per incoming class. It is designed around a curriculum that integrates artificial intelligence, digital health tools, and data analytics from the first year, rather than bolting them on as electives.

Sutter Health, one of Northern California's largest health systems, will provide clinical training sites. Santa Clara University, a Jesuit institution, will house the academic programme. The combination is unusual — a tech-adjacent billionaire, a Catholic university, and a regional hospital network — but it reflects how medical education is being reimagined in a region where healthcare and technology increasingly overlap.

Accreditation is expected to take several years. If the school opens around 2030 as planned, its first graduates would enter residency around 2034.

## The Donor

Mark Stevens made his fortune as an early investor and longtime board member of Nvidia, the chipmaker whose GPUs have become the backbone of the AI industry. His net worth is estimated at $10.5 billion. Just ten days before the medical school announcement, Stevens and his wife Mary committed $200 million to the University of Southern California to establish the Mark and Mary Stevens School of Computing and Artificial Intelligence.

The two gifts — $375 million in under a fortnight — represent one of the most concentrated bursts of philanthropy in American higher education this year. Stevens has said he sees AI and healthcare as the two domains where strategic investment can produce the largest returns for society.

## Why Silicon Valley Needs a Medical School

The Bay Area is home to Stanford Medicine, UCSF, and some of the world's leading biotech companies. Yet it has not produced a new medical school since the early twentieth century. Meanwhile, the United States faces a projected shortage of up to 86,000 physicians by 2036, according to the Association of American Medical Colleges.

California is particularly affected. Despite being the most populous state, it has fewer medical school seats per capita than many smaller states. The problem is acute in primary care: the Central Valley, for instance, has one of the lowest doctor-to-patient ratios in the country.

The Stevens school will not solve these problems alone. But its emphasis on AI-assisted diagnostics and digital health could help graduates practise more efficiently — seeing more patients, catching conditions earlier, and spending less time on administrative burden.

## The Diaspora Angle

Silicon Valley's medical community is disproportionately Indian-origin. Indian-American physicians make up roughly 10 per cent of all doctors in the United States — the largest non-white group in the profession. Many trained abroad, navigated the bruising USMLE exam pipeline, and built careers in a system that often undervalues their credentials.

A new medical school in the Bay Area, with a curriculum built around the kind of technology that Indian engineers have helped pioneer, could be a significant pipeline for the next generation of Indian-American physicians. If the school follows Santa Clara University's existing demographics, South Asian students are likely to be well represented.

For the broader diaspora, Stevens' twin bets — on AI education at USC and AI-enabled medicine in Silicon Valley — signal where philanthropic capital is heading. The intersection of technology and healthcare is no longer a niche. It is becoming the main stage.

## What to Watch

The school's success will depend on accreditation, clinical partnerships, and whether it can attract faculty from established programmes. The AI-forward curriculum is a differentiator, but medical education is conservative by nature, and regulators will scrutinise any programme that departs significantly from established models.

Still, with $175 million in founding capital and Nvidia-adjacent brainpower behind it, the Stevens School of Medicine has a shot at becoming something more than a vanity project. Silicon Valley has spent two decades trying to disrupt healthcare from the outside. This time, it is trying from within.""",
    "diaspora_angle": "Indian-American physicians make up ~10% of all US doctors. A new Bay Area medical school with AI-first curriculum, built by an Nvidia billionaire, could be a significant pipeline for the next generation of Indian-origin medical professionals.",
    "vertical": "science",
    "tags": ["Mark Stevens", "Nvidia", "Silicon Valley", "medical school", "Santa Clara University", "Sutter Health", "AI healthcare", "philanthropy"],
    "urgency": "daily",
    "sources": [
        {"url": "https://rodneyspace.com/nvidia-mark-stevens-175-million-medical-school", "name": "Rodneyspace"},
        {"url": "https://allusanewshub.com/nvidia-billionaire-mark-stevens-medical-school", "name": "USA News Hub"},
        {"url": "https://bharathorizon.com/mark-mary-stevens-175m-medical-school", "name": "Bharat Horizon"},
        {"url": "https://en.wikipedia.org/wiki/Mark_Stevens_(venture_capitalist)", "name": "Wikipedia"}
    ],
    "slug": art3_slug,
    "word_count": 750,
    "status": "published",
    "published_at": now_iso,
    "category": "technology",
    "image_entities": ["Mark Stevens", "Santa Clara University", "Silicon Valley"],
    "image_must_show": "Mark Stevens or Santa Clara University campus",
    "image_search_query": "Mark Stevens Nvidia venture capitalist",
    "score_total": 83
}

# ============================================================
# INSERT ARTICLES
# ============================================================
print("=" * 60)
print("INSERTING ARTICLES")
print("=" * 60)

for label, art in [("Bhojshala verdict", art1), ("Canada kidnapping", art2), ("Stevens medical school", art3)]:
    result = sb_post("p2_articles", art)
    if result:
        print(f"  ✓ {label}: {result[0]['id'][:8]}… — {result[0]['headline'][:60]}")
    else:
        print(f"  ✗ FAILED: {label}")

# ============================================================
# UPDATE TOPIC STATUSES
# ============================================================
print("\n" + "=" * 60)
print("UPDATING TOPIC STATUSES")
print("=" * 60)

# Topics consumed by articles (mark published)
published_topics = [
    # Bhojshala (5 topics)
    "65c76bf8-c10d-46b0-b151-aad8678bb54a",
    "484478d6-4e36-4d65-9c8e-dd63994d69fe",
    "de067311-b4a1-4ec8-9939-915e69821bb1",
    "7866d208-07a3-46dc-845c-88ad21d9cb74",
    "f6127a3c-55b9-4061-a96f-5aee903d8cb7",
    # Canada kidnapping
    "40f8da5c-ad84-4ca1-b35f-c0267d2948aa",
    # Stevens medical school
    "bdfeed8f-8dce-48c1-9a32-2bcc3d7400e5",
]

# Topics that duplicate already-published articles (reject)
rejected_topics = [
    # India-Pakistan: already covered by Army Chief article
    "58e0de45-2db4-4962-886a-b494191506c3",  # Duplicate Army Chief warning
    "278e3666-9d34-4081-b7fb-73d15037bd36",  # Rajnath warns Pakistan (related)
    "2f31e8c8-6b9d-48dc-891e-59b235c08259",  # Pakistan criticizes Army Chief (related)
    # Adani: already covered
    "b4827ac0-9ce5-4b6e-82b4-a2ff4b1785e1",  # Adani stocks surge
    "d3f27533-54e5-4110-bd08-dde9950ec53b",  # Adani nears settlement
    "3e07e233-073e-4f69-b410-3a9862c8c4fc",  # Rahul Gandhi on Adani (angle covered)
    # Rupee: already covered
    "4a7a5836-2427-44cd-b9c0-7d60327487e8",  # Rupee all-time low
    "54517ca0-c25c-4bab-8790-032d10ea8340",  # Rupee breaches 96
    # India-Netherlands: already covered
    "2f5dcaaf-8df5-4f35-8797-0911abb05ed7",  # India Netherlands partnership
    "666343df-4dc4-4155-9c00-d30223203a64",  # Dutch PM Insiya case
    # India-Pakistan Indus Waters (related to Army Chief article)
    "b57e16f5-7a27-49d9-9ee3-65b7cd23947a",  # India rejects Indus Waters ruling
    # USCIS signature rule: already covered
    # Not in our pending list but marking related
]

for tid in published_topics:
    r = sb_patch(f"p2_topics?id=eq.{tid}", {"status": "published", "updated_at": now_iso})
    if r:
        print(f"  ✓ Published: {tid[:8]}…")
    else:
        print(f"  ✗ Failed: {tid[:8]}…")

for tid in rejected_topics:
    r = sb_patch(f"p2_topics?id=eq.{tid}", {"status": "rejected", "updated_at": now_iso})
    if r:
        print(f"  ✓ Rejected: {tid[:8]}…")
    else:
        print(f"  ✗ Failed: {tid[:8]}…")

print(f"\n  Published: {len(published_topics)}, Rejected: {len(rejected_topics)}")

# ============================================================
# SCORE DECAY
# ============================================================
print("\n" + "=" * 60)
print("SCORE DECAY")
print("=" * 60)

articles = sb_get("p2_articles?status=eq.published&select=id,score_total,published_at&order=published_at.desc&limit=100")
if articles:
    now = datetime.now(timezone.utc)
    decayed = 0
    for a in articles:
        if not a.get("published_at") or not a.get("score_total"):
            continue
        pub = datetime.fromisoformat(a["published_at"].replace("Z", "+00:00"))
        age_hours = (now - pub).total_seconds() / 3600
        if age_hours < 6:
            continue
        # Decay: -2 per 6h after first 6h, floor at 20
        decay_steps = int(age_hours / 6)
        new_score = max(20, a["score_total"] - (decay_steps * 2))
        if new_score < a["score_total"]:
            sb_patch(f"p2_articles?id=eq.{a['id']}", {"score_total": new_score})
            decayed += 1
    print(f"  Decayed {decayed} articles")
else:
    print("  No articles to decay")

print("\n✅ Writer run complete")
