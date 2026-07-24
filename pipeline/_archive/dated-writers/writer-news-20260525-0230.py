#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 02:30 UTC batch
Topics: 1) Iran deal contradiction — Khamenei agreed to "broad template" per US but Tehran denies uranium commitment
        2) AI-driven tech layoffs trigger H-1B 60-day immigration crisis for Indian workers
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
# ARTICLE 1: Iran Deal Contradiction — Khamenei's "Broad Template" vs Tehran's Denial
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("iran-deal-khamenei-broad-template-uranium-tehran-denies-india-oil")
headline1_prefix = "the us says iran"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The US Says Iran's Supreme Leader Agreed to Give Up Uranium. Iran Says He Didn't. The Contradiction That Determines Whether India's Oil Crisis Ends or Deepens.",
        "subheadline": "American negotiators say Mojtaba Khamenei has signed off on the 'broad template' of a peace deal that would dispose of Iran's highly enriched uranium and reopen the Strait of Hormuz. A senior Iranian source told Reuters on Sunday that the nuclear issue is 'not part of the current deal' and 'there has been no agreement over Iran's highly enriched uranium stockpile to be shipped out of the country.' Both statements cannot be true. For India — which imports 85% of its crude oil, 60% of it through Hormuz — the distance between these two versions is the distance between an economy that stabilises and one that doesn't.",
        "slug": slug1,
        "category": "news",
        "vertical": "diplomacy",
        "diaspora_angle": "Every NRI with family in India should understand what is at stake in the gap between Washington's version of this deal and Tehran's. If the US version is accurate — Khamenei signed off, uranium goes, Hormuz reopens — then oil prices crash, India's import bill drops by billions, the rupee stabilises, inflation cools, and the relatives you send money to find their groceries, cooking gas, and petrol getting cheaper within months. If Iran's version is accurate — the nuclear issue is deferred to a final deal that could take years — then Hormuz stays contested, oil stays above $90, India keeps buying Russian crude under American sanctions pressure, and the tariff standoff that has frozen the India-US trade relationship continues indefinitely. This is not an abstract geopolitical question. The rupee at 87 to the dollar, the ₹97 cooking gas cylinder, the ₹113 petrol price in Mumbai, the flight ticket from SFO to DEL that costs $1,600 this summer — all of these are downstream consequences of whether the Strait of Hormuz is open or closed. And as of Sunday night, America and Iran cannot agree on whether the deal that would open it actually includes the hardest part.",
        "tags": ["Iran", "Khamenei", "uranium", "Strait of Hormuz", "nuclear deal", "Trump", "India oil", "Hormuz", "NRI", "energy", "diplomacy", "Reuters", "sanctions", "Mojtaba Khamenei", "peace deal"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post — Iran's supreme leader has agreed 'in principle' to give up uranium as part of peace deal, US official says", "url": "https://nypost.com/2026/05/24/us-news/irans-supreme-leader-has-agreed-in-principle-to-give-up-uranium-as-part-of-peace-deal-us-officials-says/"},
            {"name": "Reuters — Iran has not agreed to hand over highly enriched uranium stockpile, senior Iranian source tells Reuters", "url": "https://www.reuters.com/world/middle-east/iran-has-not-agreed-hand-over-highly-enriched-uranium-stockpile-senior-iranian-2026-05-25/"},
            {"name": "Reuters — Axios says proposed US-Iran deal involves opening strait during 60-day ceasefire extension", "url": "https://www.reuters.com/world/middle-east/axios-says-proposed-us-iran-deal-involves-opening-strait-during-60-day-ceasefire-extension-2026-05-24/"},
            {"name": "USA Today — Trump jabs at 'losers' criticizing Iran war peace deal", "url": "https://www.usatoday.com/story/news/politics/2026/05/25/iran-deal-trump-updates/"},
            {"name": "Washington Examiner — Netanyahu 'relieved' Trump is safe but says little about Iran deal", "url": "https://www.washingtonexaminer.com/policy/defense/netanyahu-relieved-trump-safe-iran-deal/"}
        ]),
        "score_total": 86,
        "status": "published",
        "published_at": now_iso,
        "body": """On Saturday night, a senior Trump administration official told the New York Post that American negotiators believe Iranian Supreme Leader Mojtaba Khamenei has signed off on the "broad template" of a peace deal.

"They will open up the strait in exchange for us lifting the blockade, and they will agree in principle to dispose of the highly enriched uranium," the official said. "We feel quite confident that the supreme leader has signed off on the broad template."

On Sunday, a senior Iranian source told Reuters the opposite.

"The nuclear issue will be addressed in negotiations for a final agreement and are therefore not part of the current deal," the source said. "There has been no agreement over Iran's highly enriched uranium stockpile to be shipped out of the country."

Both statements were made within hours of each other. Both were attributed to senior officials with direct knowledge of the negotiations. Both cannot be true.

## What the American Version Says

According to the Trump administration's account, the deal taking shape has three pillars.

**First**, the Strait of Hormuz reopens. Iran would clear the mines it deployed during the three-month war. Ships would pass freely with no tolls. The US would lift its naval blockade of Iranian ports.

**Second**, Iran agrees "in principle" to dispose of its roughly 1,000 pounds of highly enriched uranium. The administration's framework — reported by Axios and confirmed by multiple US officials — gives both sides 60 days to work out the logistics of how the material is removed. Trump has floated destroying it outright. He has also mentioned China as a potential partner to help dig out and transport the buried nuclear material.

**Third**, the economic architecture follows a formula the administration summarises as "no dust, no dollars." No uranium disposal, no sanctions relief. If Iran makes "significant accommodations on the enrichment question," the US will make "significant accommodations on sanctions relief." No frozen assets would be released before a final deal is signed.

The administration official cautioned that even with Khamenei's sign-off, "it is going to take days for it to filter through their system and to get an approval." The official also warned that elements inside Iran — hardliners, Revolutionary Guard commanders, bureaucrats with their own agendas — may be leaking inaccurate information to "kill this thing or derail our progress."

## What the Iranian Version Says

Iran's position, as communicated through Reuters, is structurally different. Tehran acknowledges that a preliminary agreement is being negotiated. It acknowledges that the Strait of Hormuz is on the table. But it insists that its nuclear programme — the enrichment infrastructure, the stockpile of highly enriched uranium — is **not part of the current deal**.

Iranian President Masoud Pezeshkian reinforced this position publicly. "We are ready to assure the world that we are not seeking nuclear weapons. We are not seeking instability in the region," he told reporters. But he also vowed that Iran's "negotiating team will not compromise when it counts to our country's dignity and sovereignty."

The Iranian framing separates the deal into two stages: an immediate agreement on Hormuz and a ceasefire, and a future negotiation — with no timeline — on the nuclear question. The American framing bundles them together, with the nuclear commitment as a precondition for meaningful sanctions relief.

This is not a minor difference. It is the difference between a deal and a framework for future arguments.

## Why the Gap Matters for India

India imports roughly **85% of its crude oil**. Before the Iran war, approximately **60% of that oil** transited the Strait of Hormuz. When the strait closed in March, India's energy supply chain was thrown into crisis. Crude prices spiked above $90 a barrel. India's monthly oil import bill increased by an estimated $3–4 billion. The rupee weakened. Inflation accelerated. Cooking gas prices in Indian cities hit ₹950–1,000 per cylinder.

India responded by dramatically increasing purchases of discounted Russian crude — **$46 billion worth in fiscal year 2026** — a decision that kept domestic fuel prices from spiralling but earned sharp criticism from Washington and contributed to the tariff confrontation that is still unresolved.

If the **American version** of the deal holds — Hormuz reopens, uranium is addressed, sanctions are lifted in phases — then global oil markets normalise over the next two to three months. India's import bill drops. The pressure to buy Russian crude eases. The rupee stabilises. The tariff negotiation with Washington gains space. Inflation cools. The nine crore Indian households that spend more than 10% of their income on energy get relief.

If the **Iranian version** holds — Hormuz reopens but the nuclear question is deferred indefinitely — then the deal becomes a ceasefire, not a resolution. The Strait stays open but under geopolitical uncertainty. Oil prices remain elevated because markets price in the risk of the strait closing again. India's dependence on Russian crude continues. American tariff pressure remains. The underlying economic stress on Indian households persists.

For the **4.4 million Indian Americans** watching from the US, the implications cascade through their daily lives. Gas prices at $4.56 a gallon are a direct consequence of Hormuz being closed. Flight prices to India at $1,200–1,800 are partly a consequence of jet fuel costs driven by the same crisis. The rupee at ₹87 to the dollar reflects an Indian economy under energy stress. None of these numbers change until someone resolves the contradiction between what Washington says and what Tehran says about 1,000 pounds of uranium.

## The White House Shooting and the Weekend's Chaos

The contradiction in the deal emerged during one of the more chaotic weekends of the Trump presidency. On Saturday evening, a 21-year-old man named Nasire Best — who believed he was Jesus Christ and had a history of run-ins with the Secret Service — opened fire at a White House security checkpoint. Secret Service agents killed him. A bystander was injured. Trump was in the White House at the time but was unharmed.

The shooting happened at 6:10 pm, while the Iran deal was being negotiated in real time. Trump posted about the shooting on Truth Social after midnight. By Sunday morning, he had shifted to the Iran deal, jabbing at "losers" criticising the emerging agreement and declaring he would "not rush into a deal."

The juxtaposition — a gunman at the gates, a nuclear deal in the balance, gas prices at a four-year high on Memorial Day weekend — captures a moment of American instability that the Indian diaspora experiences from a uniquely dual perspective. Many NRIs live in the Washington, DC metro area. Many work in the policy apparatus that is negotiating this very deal. And all of them are watching to see whether the contradiction at the heart of the Iran agreement resolves in favour of the version that reopens the shipping lane that keeps their homeland's economy running.

## What Happens Next

The administration says the deal could take "days" to filter through Iran's system. The 60-day window for working out the uranium logistics would begin only after both sides sign the memorandum of understanding. During that window, the Strait would be open, Iran could sell oil, and the US would negotiate over unfreezing Iranian assets.

But a senior Trump administration official also cautioned: "Whether the broad template becomes an actual agreement is still an open question."

Israel has privately conveyed unease. GOP hawks have publicly objected, warning that Iran could use Hormuz as leverage again in the future. Iranian hardliners reportedly oppose the deal's nuclear provisions — if those provisions exist at all.

For India, the calculation is simpler than the diplomacy. The Strait of Hormuz is either open or it is not. The price of oil either comes down or it does not. The summer that Indian families are trying to afford either gets cheaper or it does not.

Right now, the answer depends on which version of the deal is real. Washington's or Tehran's. The distance between the two is roughly 1,000 pounds of enriched uranium and the future of an Indian economy that cannot afford for it to stay unresolved."""
    })
    print(f"✅ Article 1 queued: {slug1}")
else:
    print(f"⏭️  Article 1 skipped (duplicate): {slug1}")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: AI Layoffs + H-1B 60-Day Immigration Crisis
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("ai-layoffs-h1b-60-day-clock-indian-tech-workers-meta-amazon")
headline2_prefix = "178,000 tech workers have been laid off"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "178,000 Tech Workers Have Been Laid Off in 2026. Most Were Replaced by AI. For the 284,000 Indians on H-1B Visas, Getting Fired Means Getting Deported.",
        "subheadline": "Meta. Amazon. LinkedIn. Oracle. Cisco. The biggest names in American technology are cutting tens of thousands of jobs — and citing AI restructuring as the reason. For American workers, a layoff means a severance package and a job search. For the 283,772 Indians who hold active H-1B visas, it means a 60-day countdown. Find a new employer willing to sponsor your visa, or leave the country. Your children's school enrolments. Your spouse's dependent visa. Your apartment lease. Your green card application that has been pending for a decade. All of it collapses if the clock runs out.",
        "slug": slug2,
        "category": "news",
        "vertical": "immigration",
        "diaspora_angle": "This is the most personal possible crisis for the Indian tech diaspora. The H-1B visa binds your right to live in America to a single employer. When that employer decides AI can do your job, you do not just lose your income — you lose your legal status. The 60-day grace period was meant to give workers breathing room. In practice, it is a ticking bomb. Indian H-1B holders account for 70% of all approved petitions. They are overrepresented in exactly the mid-level software engineering and IT operations roles that AI is displacing first. And unlike American citizens who can ride out a layoff, they cannot collect unemployment, cannot freelance, cannot start a side business while they search. They can only find another employer willing to file an H-1B transfer — in a market where 178,000 other tech workers are looking for the same jobs. Community groups in the Bay Area, Seattle, and New Jersey are organizing emergency job fairs. Immigration lawyers are fielding hundreds of calls about switching to B-2 tourist visas as a stopgap. Indian consular officials have increased outreach to affected nationals. This is not an immigration policy story. It is a story about families — real families, with kids in American schools and parents who have been paying into Social Security for fifteen years — being told they have two months to save everything they have built.",
        "tags": ["H-1B", "AI", "layoffs", "tech", "Meta", "Amazon", "LinkedIn", "Oracle", "Cisco", "Indian", "NRI", "immigration", "60-day", "deportation", "Silicon Valley", "visa", "USCIS"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Livemint — H-1B Visa Panic Grows As U.S. Tech Layoffs Put Thousands Of Indian Jobs At Risk", "url": "https://www.livemint.com/videos/h1b-visa-panic-grows-as-u-s-tech-layoffs-put-thousands-of-indian-jobs-at-risk-11779440769647.html"},
            {"name": "AIR News India — AI-Driven Layoffs in U.S. Tech Sector Trigger Immigration Crisis for Indian H-1B Workers", "url": "https://www.airnews.in/articles/bed304f0a3-ai-driven-layoffs-in-u-s-tech-sector-trigger-immigration-crisis-for-indian-h-1b-workers"},
            {"name": "Storyboard18 — 60 days or leave? US tech layoffs put Indian H-1B workers under pressure", "url": "https://www.storyboard18.com/tech/60-days-or-leave-us-tech-layoffs-put-indian-h1b-workers-under-pressure/"},
            {"name": "Storyboard18 — AI layoffs 2026: Amazon, Meta, Oracle, Cisco among tech firms cutting jobs", "url": "https://www.storyboard18.com/tech/ai-layoffs-2026-amazon-meta-oracle-cisco-tech-firms-cutting-jobs/"},
            {"name": "LinkedIn — Tech Layoffs Have Crossed 142,000 in 2026, and It's Not What Most People Think", "url": "https://www.linkedin.com/pulse/tech-layoffs-crossed-142000-2026-not-what-most-people-think/"}
        ]),
        "score_total": 85,
        "status": "published",
        "published_at": now_plus1,
        "body": """An Indian engineer at Meta's Seattle office was laid off three weeks ago. His team was dissolved as part of what the company called an "AI-led efficiency restructuring." He received a severance package. He received a LinkedIn recommendation from his manager. He also received something no American colleague had to think about: a 60-day countdown to find a new employer willing to sponsor his H-1B visa, or leave the United States.

His wife holds an H-4 dependent visa. His daughter is finishing third grade at a public school in Redmond. His green card application, filed under the EB-2 category, has been pending for seven years. If he does not find a new sponsor within 60 days, all of it — the visa, the dependent status, the school enrolment, the green card queue position — collapses.

His story, shared widely on X this month, is not unique. It is the new normal.

## The Numbers

According to Layoffs.fyi, over **178,000 tech workers** have been laid off across more than 70 companies in 2026. The tracker at NBot.ai puts the AI-specific white-collar cut figure at **131,000**. The companies doing the cutting are not struggling startups. They are the largest, most profitable technology firms on earth.

**Meta** has cut multiple rounds this year, restructuring teams around AI-driven products and reducing headcount in areas where automation can replace human work. **Amazon** has eliminated thousands of positions across its cloud, retail, and logistics divisions. **LinkedIn** — owned by Microsoft — announced layoffs in its engineering division. **Oracle**, **Cisco**, **Intuit**, and **Cloudflare** have all conducted significant reductions tied explicitly to AI integration.

A Resume.org survey found that **44% of US hiring managers** cite AI as a top driver of expected layoffs this year. A LinkedIn analysis noted that companies invested **$750 billion in AI infrastructure and data centres in 2026** — while simultaneously reducing headcount. The message is explicit: the money that used to pay for engineers is being redirected to pay for the systems that replace engineers.

## Why Indians Bear the Brunt

Of the **406,348 H-1B petitions** approved by USCIS in fiscal year 2025, **283,772 — or 70%** — went to Indian nationals. Indians are not just the largest group on H-1B visas. They are the dominant group, by a margin that dwarfs every other nationality combined.

They are also concentrated in precisely the roles that AI is displacing first. Mid-level software engineers. QA engineers. IT operations specialists. Data analysts. DevOps engineers who manage deployment pipelines. These are the positions that large language models, code-generation tools, and AI-powered automation platforms are making redundant — not in theory, but in practice, in the restructuring plans being executed right now.

The H-1B visa ties a worker's legal right to live in America to a specific employer. When that employer eliminates your position, you have **60 days** to find a new employer willing to file an H-1B transfer petition. During those 60 days, you cannot work. You cannot collect unemployment insurance. You cannot freelance, consult, or start a business. You can only search.

In a normal labour market, 60 days might be adequate. In a market where 178,000 other tech workers — many of them American citizens who can be hired without visa paperwork — are competing for the same shrinking pool of positions, 60 days is a death sentence for a significant number of Indian H-1B holders.

## The Cascading Consequences

The 60-day clock does not just affect the worker. It affects the entire family structure that Indian immigrants build over years in America.

**Spouses on H-4 dependent visas** lose their status when the H-1B holder loses theirs. If the spouse has work authorisation under the H-4 EAD programme — something that took its own years-long battle to obtain — that authorisation evaporates. Families go from two incomes to zero incomes and zero legal status simultaneously.

**Children enrolled in American schools** face withdrawal. A family that has lived in Cupertino or Cary or Edison for a decade — whose children speak with American accents, play American sports, have American friends — must contemplate pulling them out mid-year and relocating to a country those children may barely know.

**Green card applications** that have been pending for five, ten, or fifteen years do not survive a gap in legal status. The EB-2 and EB-3 backlogs for Indian nationals are measured in decades. If you fall out of status, you go back to the end of the line — or you leave entirely and abandon the application. Years of filing fees, legal costs, and patient waiting are erased by a single layoff notification.

**Housing and financial obligations** do not pause. The mortgage on the house in Fremont. The lease on the apartment in Bellevue. The car payments. The 529 college savings plans. American financial life is built on the assumption of continued income and continued residence. The 60-day clock shatters both assumptions simultaneously.

## What the Community Is Doing

Indian-American community organisations have responded with urgency. Professional networks in the Bay Area, Seattle, and the New Jersey-New York corridor are organising **emergency job fairs** specifically for laid-off H-1B holders. Immigration lawyers report being flooded with calls about contingency options.

The most common question: **can I switch to a B-2 tourist visa?** In theory, yes — a change of status from H-1B to B-2 can buy time. In practice, immigration lawyers report **increased scrutiny and declining approval rates** for these conversions. USCIS has not issued new policy guidance on H-1B extensions or grace period adjustments in response to the layoff wave.

**Indian consular officials** in the US have increased outreach to affected nationals, though the consulate's ability to intervene in US immigration matters is limited. The response has been largely informational — connecting displaced workers with legal resources and community groups.

Some workers are exploring **self-petitioned alternatives**: the O-1 extraordinary ability visa, the EB-1A green card category, or returning to India to work for the same company's Global Capability Centre (GCC). India now hosts **55% of the world's GCCs** — the R&D and engineering arms of the same companies doing the laying off. The irony is not lost on anyone: the same company that fired you in Sunnyvale may want to hire you in Bengaluru, at a fraction of the salary, to do similar work.

## The AI Irony

The deeper irony cuts to the bone. Indian engineers helped build the AI systems that are now eliminating their jobs.

The training data for large language models was labelled in significant part by workers in India. The research teams at OpenAI, Google DeepMind, and Anthropic include dozens of IIT and IISc graduates. India contributes **23% of all AI-related code on GitHub** — more than any other country.

The technology that Indian talent helped create is now being deployed by their employers to justify their elimination. The companies are not doing this out of malice. They are doing it because the economics are irresistible. An AI system that can write, test, and deploy code does not need an H-1B visa. It does not need health insurance. It does not take paternity leave. It does not have a green card application that costs the company legal fees.

## The Policy Vacuum

Congress has not acted. USCIS has issued no emergency guidance. The Trump administration — which has simultaneously slowed green card processing, killed the adjustment of status pathway, and called green card applications an "extraordinary act of grace" — has offered no relief to the wave of H-1B holders losing status through no fault of their own.

Senator Bernie Sanders warned last week that AI and robotics are poised to become "the most transformative economic revolution in the history of this country." California Governor Gavin Newsom issued an executive order calling for state agencies to address AI-driven workforce displacement. But federal immigration policy — the policy that determines whether 283,772 Indian professionals can remain in this country — has not budged.

The H-1B programme was designed in 1990 for a world where employers needed workers and workers needed employers. It was not designed for a world where employers need AI and workers need a country. The 60-day grace period was added in 2017 as a humanitarian measure. Nine years later, it is the countdown clock on which hundreds of thousands of Indian lives in America depend.

## What It Means

This Memorial Day weekend, as 45 million Americans travel and complain about $4.56 gas, an unknown number of Indian tech workers are sitting in apartments in Mountain View and Redmond and Jersey City with a different kind of countdown running. They are not planning summer vacations. They are planning whether they still live here in August.

The AI revolution that America celebrates as innovation and efficiency has a human cost. That cost is measured in 60-day increments, in school withdrawal forms, in one-way flights to Bengaluru booked in June, and in green card applications abandoned after a decade of waiting.

For the Indian diaspora, this is not an industry trend or a policy debate. It is the story of a generation that came to America on the promise of a visa programme, built careers and families and mortgages on that promise, and is now watching the promise be broken — not by Congress, not by executive order, but by a machine learning model that learned to code."""
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

print("\n✅ Writer pipeline complete")
