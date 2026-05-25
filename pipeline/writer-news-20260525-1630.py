#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-25 16:30 UTC batch
Topics: 1) Nancy Mace's constitutional amendment to ban foreign-born people from Congress — directly targets two Indian-born lawmakers
        2) FIFA World Cup 2026 starts in 17 days and India still has no broadcaster — rights collapsed from $100M to $35M
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

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
    """Search Pexels for a relevant photo, return URL or None."""
    if not PEXELS_KEY:
        print("  ⚠ No Pexels key found")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            r = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_KEY},
                params={"query": q, "per_page": 5, "orientation": "landscape"},
                timeout=15
            )
            if r.status_code == 200:
                photos = r.json().get("photos", [])
                if photos:
                    url = photos[0]["src"]["large2x"]
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None

def upload_image_to_supabase(image_url, filename):
    """Download image and upload to Supabase storage, return public URL."""
    try:
        img_data = requests.get(image_url, timeout=20).content
        content_type = "image/jpeg"
        upload_url = f"{SB_URL}/storage/v1/object/article-images/{filename}"
        h = {
            "apikey": SB_KEY,
            "Authorization": f"Bearer {SB_KEY}",
            "Content-Type": content_type,
            "x-upsert": "true",
        }
        r = requests.post(upload_url, headers=h, data=img_data, timeout=30)
        if r.status_code in (200, 201):
            public_url = f"{SB_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {filename}")
            return public_url
        else:
            print(f"  ⚠ Upload failed ({r.status_code}): {r.text[:200]}")
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
    return image_url  # Fall back to original URL

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
# ARTICLE 1: Nancy Mace's Constitutional Amendment Targeting Foreign-Born Lawmakers
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("nancy-mace-ban-foreign-born-congress-pramila-jayapal-shri-thanedar-india")
headline1_prefix = "nancy mace"
if slug1 not in existing_slugs and not any(headline1_prefix in h for h in existing_headlines_lower):
    body1 = """On Wednesday, Representative Nancy Mace of South Carolina stood at a podium and proposed a constitutional amendment that would bar every naturalized American citizen from serving in the United States Congress, the federal judiciary, or any Senate-confirmed position in the executive branch.

She named three people. "Ilhan Omar. Shri Thanedar. Pramila Jayapal," Mace posted on X. "All born in foreign countries, none were citizens by birth. All sitting in the United States Congress. All making clear every single day their loyalty is not to America."

Two of the three people she named were born in India.

## Who Mace Is Targeting

Pramila Jayapal represents Washington's 7th Congressional District, which includes Seattle. She was born in Chennai in 1965, moved to the United States at 16, and became a citizen in 2000. Before entering Congress in 2017, she founded the largest immigrant rights organization in Washington state. She is the first Indian American woman elected to the House of Representatives and now chairs the Congressional Progressive Caucus.

Shri Thanedar represents Michigan's 13th Congressional District, covering most of Detroit. He was born in Belgaum, Karnataka, in 1955. He came to the United States on a student visa, earned a Ph.D. in chemistry from the University of Akron, built and sold multiple businesses, and became a citizen. He was elected to Congress in 2022 after serving in the Michigan state legislature.

The third target, Ilhan Omar, was born in Somalia and represents Minnesota's 5th District. She became a citizen in 2000.

## The Numbers Behind the Proposal

Currently, 26 members of the House of Representatives were born outside the United States — 19 Democrats and 7 Republicans. The Constitution already requires that only the president and vice president be natural-born citizens. Every other elected or appointed federal official can be a naturalized citizen, provided they meet the residency and citizenship duration requirements specific to their office.

A constitutional amendment requires two-thirds approval in both the House and Senate, followed by ratification by 38 of the 50 state legislatures. The last constitutional amendment — the 27th, restricting Congressional pay raises — was ratified in 1992, and it had been originally proposed in 1789. By any measure, Mace's proposal is dead on arrival as legislation. But that is not why it matters.

## Why This Is Not Just About Omar

The framing of Mace's proposal is the story. She did not say these legislators had broken laws, violated ethics, or committed acts against the country. She said their "loyalty is not to America." The accusation is not about conduct. It is about origin.

"If you hold power in the American government, you should be a natural-born American citizen," Mace said. "For too long we have allowed foreign-born members to hold seats in this government, while making clear their loyalty is not here. We see it every day."

The word "allowed" is doing extraordinary work in that sentence. The United States did not "allow" Jayapal and Thanedar to hold their seats through some bureaucratic oversight. Voters elected them. In Jayapal's case, by margins exceeding 80 percent. In Thanedar's case, after a competitive primary in one of the most politically active districts in the country. What Mace is proposing is not a correction to a loophole. It is a redefinition of who counts as American enough to serve.

Vice President JD Vance added a separate dimension the same week, indicating to reporters that Omar faces "some sort of investigation" related to her immigration status — a claim Omar flatly denied, calling Vance "delusional."

## What This Means for the Indian Diaspora

Indian Americans are the most highly naturalized immigrant group in the United States. According to the Migration Policy Institute, approximately 74 percent of Indian-born immigrants who are eligible for naturalization have completed the process — well above the national average of 65 percent. They do not naturalize reluctantly. They study for the citizenship test. They attend the ceremonies. They bring their families.

The Indian American community has, in the span of one generation, produced two members of Congress born in India, a vice presidential candidate (Vivek Ramaswamy, born in the US to Indian immigrants), a former vice presidential nominee and sitting vice president (Kamala Harris, half-Indian), a former governor (Nikki Haley, born in the US to Indian immigrants), and the CEOs of Google, Microsoft, IBM, and Adobe. The community's civic engagement is not a question — it is a statistical fact.

What Mace's amendment says to that community is this: Your naturalization was incomplete. Your oath was provisional. Your citizenship certificate is a different grade of document than a birth certificate. You can pay taxes, start companies, employ Americans, send your children to serve in the military, and win elections — but your loyalty will always be in question because you were not born here.

This is not an abstract constitutional debate. It is a direct challenge to the foundational premise that naturalization means equality.

The proposal will not pass. It will not receive a committee hearing. It will not get a floor vote. But for the 4.8 million Indian Americans in the United States — and for the hundreds of thousands who are currently navigating the citizenship process through green card backlogs, H-1B waits, and EB-2 queues that stretch back to 2013 — the message is not in the legislation. It is in the fact that a sitting member of Congress can point to two people born in India and publicly declare that their loyalty is not to America, and the political cost of doing so is, apparently, zero.

## The Deeper Contradiction

The same week that Mace proposed barring Indian-born Americans from Congress, Secretary of State Marco Rubio was in New Delhi telling India that the United States values its "strategic partnership" and that American immigration reform is "not targeted at India." He urged Indians to be patient during the "period of transition."

Rubio acknowledged on camera that the reforms are having a "disproportionate impact on a place like India that provides so many high-skilled workers to the U.S. economy." He addressed anti-Indian racism by telling Indian journalists that "every country in the world has stupid people."

The juxtaposition is precise. At the diplomatic level, India is a strategic partner whose people are valued. At the legislative level, a member of Congress can propose stripping the civic rights of Indian-born Americans and frame it as patriotism. The Indian diaspora does not live in one of these realities. It lives in both, simultaneously.

External Affairs Minister S. Jaishankar, sitting alongside Rubio, noted that India expects "legal mobility would not be adversely impacted." He was talking about visas. But the underlying concern extends further. If the political environment has shifted to a point where a constitutional amendment targeting naturalized citizens is introduced without meaningful backlash — even if it has no legislative future — what does that say about where the next four years are headed?

For Indian Americans, the answer is not in the text of the amendment. It is in the silence that followed it."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "A Congresswoman Just Proposed Banning Every Naturalized Citizen From Serving in Congress. She Named Two Indian-Born Lawmakers by Name. She Said Their Loyalty 'Is Not to America.'",
        "subheadline": "Representative Nancy Mace of South Carolina introduced a constitutional amendment last week that would bar all foreign-born Americans — including naturalized citizens — from serving in Congress, the federal judiciary, or any Senate-confirmed position. She specifically named Pramila Jayapal (born in Chennai, India), Shri Thanedar (born in Belgaum, Karnataka), and Ilhan Omar (born in Somalia). 'All born in foreign countries, none were citizens by birth,' Mace wrote on X. 'All making clear every single day their loyalty is not to America.' The amendment has no realistic path to passage — it would require two-thirds of Congress and ratification by 38 states — but its introduction, in the same week that Secretary of State Rubio was in New Delhi praising India as a 'great ally,' crystallizes a contradiction that 4.8 million Indian Americans navigate daily: valued as workers and investors, questioned as citizens.",
        "slug": slug1,
        "category": "news",
        "vertical": "immigration",
        "diaspora_angle": "If you are an Indian American who took the citizenship oath, memorized the amendments, and stood in a courtroom while a judge told you that you are now equal to every American born on this soil — Nancy Mace just told you that is not how she sees it. Two of the three people she named were born in India. Pramila Jayapal arrived from Chennai at 16. Shri Thanedar came from Belgaum on a student visa, built multiple businesses, and won an election in Detroit. Their paths are the Indian American success story in concentrated form: immigration, education, enterprise, civic engagement. Mace's proposal says none of that matters because they were not born here. Indian Americans are the most highly naturalized immigrant group in the United States — 74 percent of those eligible have become citizens. They do not naturalize casually. They wait in decade-long green card queues, they pay thousands in fees, they take the test, they bring their families to the ceremony. What the Mace amendment says to every Indian who has done this — or is currently doing this — is that your naturalization was conditional. Your oath was decorative. Your citizenship is a different class of document. The amendment will not pass. But the fact that a sitting member of Congress can name two Indian-born Americans, question their loyalty on a public platform, and face no political consequence — that is the part that does not require a constitutional amendment to matter.",
        "tags": ["Nancy Mace", "constitutional amendment", "Pramila Jayapal", "Shri Thanedar", "naturalized citizens", "Indian Americans", "Congress", "foreign-born", "immigration", "loyalty", "citizenship", "Rubio", "India", "NRI", "H-1B", "green card"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post — Rep. Ilhan Omar shrugs off Nancy Mace bill to ban foreign-born pols from Congress", "url": "https://nypost.com/2026/05/25/us-news/omar-confronted-on-camera-over-gop-proposal-targeting-foreign-born-lawmakers-good-luck-to-her/"},
            {"name": "Fox News — Rubio pushes back on India's visa curbs concerns, says policy must be 'America First'", "url": "https://foxnews.com/politics/rubio-pushes-back-indias-concerns-us-visa-curbs-says-policy-must-america-first-trump"},
            {"name": "Fox News — Omar confronted on camera over GOP proposal targeting foreign-born lawmakers", "url": "https://www.foxnews.com/politics/omar-confronted-camera-gop-proposal-targeting-foreign-born-lawmakers"},
            {"name": "Migration Policy Institute — Indian Immigrants in the United States", "url": "https://www.migrationpolicy.org/article/indian-immigrants-united-states"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: Mace amendment targeting Indian-born lawmakers")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: FIFA World Cup Starts in 17 Days — India Has No Broadcaster
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("fifa-world-cup-2026-india-no-broadcaster-rights-crisis-zee-doordarshan")
headline2_prefix = "fifa world cup"
if slug2 not in existing_slugs and not any(headline2_prefix in h for h in existing_headlines_lower):
    body2 = """The FIFA World Cup 2026 begins on June 11 in Mexico City. Forty-eight teams will play 104 matches across 16 stadiums in the United States, Canada, and Mexico over 39 days. It is the largest World Cup in history. Fox Sports has the American rights. Telemundo has the Spanish-language rights. China's state broadcaster CMG finalized its deal on May 15. The BBC and ITV will split coverage in the UK. Every major football market in the world has a confirmed broadcaster.

Except India.

With seventeen days to go, the world's most populous country — 1.4 billion people, a football fanbase that FIFA itself has estimated at 745 million engagements — does not know whether it will be able to watch the World Cup. This is not a negotiation delay. This is a crisis that has been building for months, has now reached the Delhi High Court, and involves a price collapse so dramatic that it tells a broader story about India's place in the global sports economy.

## How the Price Fell from $100 Million to $35 Million

FIFA initially valued the Indian subcontinent media rights package — covering both the 2026 and 2030 World Cups — at approximately $100 million. That figure was based on projections of India's growing football audience, the success of the Indian Super League, and the country's overall trajectory as a sports media market.

No one bid $100 million.

Sony, which held the previous cycle's rights, passed. Star Sports, part of the Walt Disney empire that had just restructured its India operations into JioHotstar through a merger with Reliance's Jio Cinema, submitted a bid of approximately $20 million — a fifth of the asking price. Prasar Bharati, India's public broadcaster, said it wasn't its responsibility to acquire commercial sports rights and stepped away from the table.

FIFA slashed its expectations to $35 million. Even at that price, negotiations dragged. JioHotstar maintained its $20 million position. Zee Entertainment emerged as a late contender, and reports from multiple Indian sports media outlets suggest that a deal is "nearly finalized" — but as of today, there is no signed contract, no announcement, and no broadcast schedule.

Former AIFF General Secretary Shaji Prabhakaran told media on May 23 that negotiations are "complete" and an announcement is "likely to be made next week." FIFA has said only that discussions "are ongoing and must remain confidential at this stage."

## The Delhi High Court Steps In

The situation has become so dire that advocate Avdhesh Bairwa filed a writ petition under Article 226 of the Constitution, asking the court to direct Prasar Bharati to ensure the tournament is broadcast on free-to-air platforms — specifically Doordarshan and DD Sports.

Justice Purushaindra Kumar Kaurav issued notice to the Centre and Prasar Bharati. The petition argues that depriving millions of Indian football fans from watching one of the world's biggest sporting events violates the public's right to access events of national importance.

India's Sports Broadcasting Signals (Mandatory Sharing with Prasar Bharati) Act of 2007 was designed for exactly this scenario — it requires that sporting events of "national importance" be made available on free-to-air television. But the Act requires someone to have the rights first before they can be shared. Without a primary rightsholder, there is nothing to share.

## An Indian-American Firm Enters the Picture

In a development that has added both intrigue and confusion, an Indian-American investment firm from Washington, DC — Avni LLC — announced on May 21 that it had submitted a corporate guarantee backed by "financial commitments exceeding $300 million" as part of FIFA's closed tender process for the Indian subcontinent.

Avni LLC claims an "associated partner" secured the winning bid after competing against several major Indian broadcasters. Deelip Mhaske, the firm's President and CEO, described a vision "beyond traditional television — one built around OTT platforms, AI-powered multilingual broadcasting, mobile micro-subscriptions and esports integrations across Asia."

FIFA has not confirmed Avni's claim. Indian broadcasting industry sources have treated the announcement with skepticism. If the claim is legitimate, it would represent a remarkable scenario: an Indian diaspora company, based in the American capital, controlling the World Cup broadcast rights for the country those diaspora members left.

## What This Says About India as a Sports Market

The collapse of the rights value — from $100 million to possibly $35 million — is not a reflection of Indian football's popularity. It is a reflection of India's sports economics.

Cricket remains the overwhelmingly dominant commercial sport. The IPL's 2023-2027 media rights sold for $6.2 billion. A single IPL match draws more viewers than most FIFA World Cup group stage games. Advertisers and broadcasters allocate their Indian sports budgets around cricket seasons, leaving relatively little room for football, which occupies a passionate but commercially secondary position.

The World Cup also has a scheduling problem in India. Matches in North American time zones will air in the early morning hours IST — prime viewing times in Los Angeles and New York translate to 2 AM and 5:30 AM in Mumbai and Delhi. This was a factor in Sony's decision not to renew, in Prasar Bharati's reluctance to bid, and in the overall soft market.

## The Diaspora Irony

The FIFA World Cup 2026 is being hosted in the United States, Canada, and Mexico — the three countries with the largest Indian diaspora populations in the Western hemisphere. Matches will be played in New York, Los Angeles, Houston, Dallas, San Francisco, Seattle, Boston, Philadelphia, Miami, Atlanta, and Kansas City — cities with substantial Indian American populations.

Indian Americans can buy tickets. They can drive to the stadiums. They can watch every match on Fox, Telemundo, or any number of streaming platforms available in the US. Some already have tickets.

Their parents in India may not be able to watch at all.

The scenario is almost absurdist: an Indian American family in Houston attends a World Cup match live at NRG Stadium. They FaceTime their parents in Hyderabad. The parents cannot watch the same match on any Indian television channel because no one has bought the rights.

If the Zee deal closes this week, the crisis may be averted at the last minute. But the fact that it came to this — that India needed a court petition and a price collapse of 65 percent before a broadcaster could be found, seventeen days before the biggest sporting event on earth — says something about the gap between India's aspirations as a global sporting power and the commercial reality of its sports media market.

India is bidding to host the 2036 Olympics. It hosted the FIFA U-17 World Cup in 2017. The Indian Super League is growing. The country has the audience. What it does not yet have is the infrastructure of value — the advertising ecosystem, the prime-time scheduling, the corporate willingness to pay premium prices — that makes hosting and broadcasting global events commercially sustainable.

The World Cup will start on June 11 regardless. The question is whether 1.4 billion people will be able to see it."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "The FIFA World Cup Starts in Seventeen Days. India — Population 1.4 Billion, Football Fanbase 745 Million — Still Has No Broadcaster. The Rights Collapsed from $100 Million to $35 Million. A Delhi Court Has Had to Step In.",
        "subheadline": "With the largest World Cup in history set to kick off on June 11 in Mexico City, every major football market in the world has a confirmed broadcaster except India. FIFA's initial asking price of $100 million for the Indian subcontinent found no takers. Sony passed. Disney-Reliance's JioHotstar bid $20 million. Doordarshan said it wasn't its job. FIFA slashed the price to $35 million. Zee Entertainment has reportedly emerged as a late frontrunner, and an Indian-American investment firm from Washington, DC, has claimed to have won the bid with $300 million in commitments — a claim FIFA has not confirmed. The Delhi High Court has issued notices after a citizen petition demanding free-to-air coverage. The tournament will be played across 16 American, Canadian, and Mexican cities where millions of NRIs live and can watch every match. Their families in India may not be able to see a single game.",
        "slug": slug2,
        "category": "news",
        "vertical": "sports",
        "diaspora_angle": "Here is the absurdity of the situation: the FIFA World Cup 2026 is being hosted in the United States. Matches will be played in Houston, Dallas, Los Angeles, New York, San Francisco, Seattle, Boston, Philadelphia, Miami, Atlanta, and Kansas City — every one of those cities has a significant Indian American population. Indian Americans can buy tickets. Some already have. They can watch every match on Fox or Telemundo or half a dozen streaming platforms. But their parents in Pune, their cousins in Lucknow, their grandparents in Coimbatore — they may not be able to watch a single match on Indian television, because with 17 days to go, no one has bought the rights. The price tells the story. FIFA valued the Indian rights at $100 million. No one wanted them at that price. Or at $60 million. Or at $50 million. The market settled around $35 million — a 65 percent collapse — and even then, it took until the last possible moment for a deal to potentially close. For the diaspora, this is both embarrassing and clarifying. India aspires to host the 2036 Olympics. It dreams of being a global sporting power. But the commercial reality is that Indian sports broadcasting infrastructure cannot support a global football tournament that airs at 2 AM IST in the group stages. Cricket owns the sports economy so completely that the world's biggest sporting event could not find a buyer at one-third of the asking price. If you are an NRI watching this from your American living room — with the match on your 65-inch TV, the stadium 45 minutes away, and your WhatsApp group silent because no one at home can see what you are seeing — you are living the gap between what India says it is and what India's market will pay for.",
        "tags": ["FIFA", "World Cup 2026", "India", "broadcast rights", "Zee", "JioHotstar", "Doordarshan", "Prasar Bharati", "Delhi High Court", "cricket", "football", "NRI", "sports media", "Avni LLC", "diaspora"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "The Indian Eye — Indian American Firm claims FIFA India rights", "url": "https://theindianeye.com/2026/05/21/indian-american-firm-claims-fifa-india-rights/"},
            {"name": "Inshorts — FIFA nears $35M India broadcast deal for 2026 World Cup", "url": "https://inshorts.com/en/news/fifa-nears-35-mn-india-broadcast-deal-for-2026-world-cup-report"},
            {"name": "Exchange4Media — FIFA set to close India media rights deal soon", "url": "https://exchange4media.com/media-others-news/fifa-set-to-close-india-media-rights-deal-for-world-cup-soon-report"},
            {"name": "Fox News — Rubio pushes back on India visa curbs, America First", "url": "https://foxnews.com/politics/rubio-pushes-back-indias-concerns-us-visa-curbs-says-policy-must-america-first-trump"},
            {"name": "Sporting News — Who will broadcast FIFA World Cup 2026 in India?", "url": "https://www.sportingnews.com/in/football/news/who-broadcast-fifa-world-cup-2026-india/"}
        ]),
        "score_total": 84,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: FIFA World Cup India broadcast crisis")
else:
    print(f"✗ Article 2 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# PUBLISH + IMAGE SOURCING
# ══════════════════════════════════════════════════════════════

if not articles:
    print("\n⚠ No new articles to publish. Exiting.")
    exit(0)

print(f"\n📝 Publishing {len(articles)} articles...")

for i, art in enumerate(articles):
    art_id = art["id"]
    print(f"\n--- Article {i+1}: {art['headline'][:80]}...")

    # Insert article
    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # Fetch image
    if i == 0:
        img_url = fetch_pexels_image("US Capitol building Congress", "American government building")
    else:
        img_url = fetch_pexels_image("football stadium fans", "soccer world cup stadium")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {"image_url": final_url})
            print(f"  ✓ Image linked")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
    # Decay articles older than 7 days to score 35
    old_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=7)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.35",
        "limit": "200"
    })
    for a in old_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 35})
    print(f"  Decayed {len(old_arts)} articles (>7d → 35)")

    # Decay articles 3-7 days old to score 50
    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
    # Filter out the >7d ones already decayed
    mid_arts = [a for a in mid_arts if a["id"] not in {x["id"] for x in old_arts}]
    for a in mid_arts:
        sb_patch("p2_articles", {"id": f"eq.{a['id']}"}, {"score_total": 50})
    print(f"  Decayed {len(mid_arts)} articles (3-7d → 50)")
except Exception as e:
    print(f"  ⚠ Decay error: {e}")

# ══════════════════════════════════════════════════════════════
# GIT COMMIT + PUSH
# ══════════════════════════════════════════════════════════════

print("\n📦 Committing and pushing...")
repo_dir = Path.home() / "workspace" / "the-videshi-news"
try:
    subprocess.run(["git", "add", "-A"], cwd=repo_dir, capture_output=True, timeout=15)
    result = subprocess.run(
        ["git", "commit", "-m", f"news: Mace amendment + FIFA India broadcast crisis ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
        cwd=repo_dir, capture_output=True, text=True, timeout=15
    )
    print(f"  Commit: {result.stdout.strip()[:100]}")
    push = subprocess.run(["git", "push"], cwd=repo_dir, capture_output=True, text=True, timeout=30)
    if push.returncode == 0:
        print("  ✓ Pushed to main → Vercel auto-deploy")
    else:
        print(f"  ⚠ Push issue: {push.stderr[:200]}")
except Exception as e:
    print(f"  ⚠ Git error: {e}")

print("\n✅ News writer batch complete.")
