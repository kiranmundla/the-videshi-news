#!/usr/bin/env python3
"""News writer for The Videshi — 2026-05-30 batch"""

import json
import os
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone

# Load Supabase config
env_vars = {}
with open(os.path.expanduser("~/.env.supabase")) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            if line.startswith("export "):
                line = line[7:]
            key, val = line.split("=", 1)
            val = val.strip().strip("'").strip('"')
            env_vars[key] = val

SUPABASE_URL = env_vars["SUPABASE_URL"]
SUPABASE_KEY = env_vars["SUPABASE_SERVICE_ROLE_KEY"]

# Load Pexels key
pexels_key = ""
pexels_env = os.path.expanduser("~/workspace/.env.pexels")
if os.path.exists(pexels_env):
    with open(pexels_env) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                if line.startswith("export "):
                    line = line[7:]
                key, val = line.split("=", 1)
                val = val.strip().strip("'").strip('"')
                if "PEXELS" in key.upper():
                    pexels_key = val
                    break


def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        req = urllib.request.Request(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None


def fetch_pexels_image(query, fallback_query=None):
    """Fetch an image from Pexels API using curl (urllib gets 403)."""
    if not pexels_key:
        print("  ⚠ No Pexels API key found")
        return None

    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            result = subprocess.run(
                ["curl", "-sS", f"https://api.pexels.com/v1/search?query={urllib.parse.quote(q)}&per_page=5&orientation=landscape",
                 "-H", f"Authorization: {pexels_key}"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("large")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def validate_image(url):
    """Validate image URL returns HTTP 200 with image content type and reasonable size."""
    if not url:
        return False
    try:
        req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            content_type = resp.headers.get("Content-Type", "")
            content_length = int(resp.headers.get("Content-Length", "0"))
            if "image" in content_type and content_length > 5000:
                print(f"  ✓ Image validated: {content_type}, {content_length} bytes")
                return True
            else:
                print(f"  ⚠ Image validation failed: type={content_type}, size={content_length}")
                return False
    except Exception as e:
        print(f"  ⚠ Image validation error: {e}")
        # For Wikipedia/Pexels, assume valid if HEAD fails (some servers block HEAD)
        if "upload.wikimedia.org" in url or "images.pexels.com" in url:
            return True
        return False


def publish_article(article):
    """Publish article to Supabase."""
    payload = json.dumps(article)
    try:
        result = subprocess.run(
            ["curl", "-sS", "-X", "POST",
             f"{SUPABASE_URL}/rest/v1/p2_articles",
             "-H", f"apikey: {SUPABASE_KEY}",
             "-H", f"Authorization: Bearer {SUPABASE_KEY}",
             "-H", "Content-Type: application/json",
             "-H", "Prefer: return=representation",
             "-d", payload],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0 and ('"id"' in result.stdout or '"headline"' in result.stdout):
            print(f"  ✓ Published: {article['headline'][:60]}...")
            return True
        else:
            print(f"  ✗ Publish failed: {result.stdout[:200]}")
            print(f"    stderr: {result.stderr[:200]}")
            return False
    except Exception as e:
        print(f"  ✗ Publish error: {e}")
        return False


# ============================================================
# ARTICLES
# ============================================================

now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

articles = []

# ------------------------------------------------------------------
# Article 1: Vinesh Phogat — Supreme Court allows Asian Games trials
# ------------------------------------------------------------------
print("\n=== Article 1: Vinesh Phogat SC ruling ===")
vinesh_image = fetch_wikipedia_person_image("Vinesh Phogat")
if not vinesh_image:
    vinesh_image = fetch_wikipedia_person_image("Vinesh Phogat (wrestler)")
if vinesh_image and not validate_image(vinesh_image):
    vinesh_image = None
if not vinesh_image:
    vinesh_image = fetch_pexels_image("wrestling competition mat", "Indian wrestler Olympic")
    if vinesh_image and not validate_image(vinesh_image):
        vinesh_image = None

articles.append({
    "headline": "Supreme Court Allows Vinesh Phogat to Compete in Asian Games Trials. Then It Warned Courts to Stay Out of Sports.",
    "subheadline": "The apex court cleared the wrestler for selection trials beginning May 30 but delivered a pointed rebuke about judicial overreach in sporting events",
    "body": """The Supreme Court on Friday cleared the way for star wrestler Vinesh Phogat to participate in the selection trials for the 2026 Asian Games, ending weeks of legal uncertainty — but not before delivering a sharp warning about courts involving themselves in competitive sports.

## 'She Has Made the Country Proud'

A bench hearing the case acknowledged Phogat's stature as one of India's most decorated wrestlers. "Had it been someone else, the matter would have been different. She has made the country proud," the court observed during the hearing.

The ruling overturned a challenge by the Wrestling Federation of India, which had contested a Delhi High Court order permitting Phogat to take part in the trials. With the Supreme Court's blessing, Phogat became eligible to compete in the selection process that begins on May 30.

But the bench made clear this was not an invitation for litigants to drag every sporting dispute into the judiciary. Justice PS Narasimha delivered some of the most pointed remarks. "This is not a medical college admission matter. These are national and international sporting events. Courts should not intervene in such cases in a manner that disrupts the entire schedule," he said.

The court told Phogat directly: "You are a brilliant athlete, but the nation comes first."

## A Career Defined by Controversy and Triumph

Phogat's career has been a study in extremes. She won gold at the 2018 Asian Games in Jakarta, became the first Indian woman wrestler to reach an Olympic final at the Paris 2024 Games, and has been a consistent medal contender at the World Championships.

But Paris ended in heartbreak. Phogat was disqualified from the gold medal match after missing weight by a reported 100 grams — a decision that triggered a prolonged legal battle at the Court of Arbitration for Sport and became a national talking point for weeks. The CAS ultimately rejected her appeal, and the saga left deep scars on her relationship with wrestling's governing bodies.

Since then, Phogat briefly entered politics, winning a seat in the Haryana state assembly as a Congress candidate in the October 2024 elections. She resigned to return to competitive wrestling in early 2026, setting the stage for the latest confrontation with the federation.

## The Federation's Objection

The Wrestling Federation of India had argued that Phogat had not met the eligibility criteria for the Asian Games selection trials, citing her period away from competitive wrestling and questions about her compliance with anti-doping testing requirements during her time in politics.

The Delhi High Court had sided with Phogat, ruling that excluding a decorated athlete from trials without clear procedural grounds would be unjust. The federation then appealed to the Supreme Court.

By clearing Phogat's participation while simultaneously cautioning against judicial intervention in sports, the Supreme Court effectively split the difference — allowing the wrestler her shot while signaling that the judiciary would not become a permanent referee in federation disputes.

## What the Asian Games Trials Mean

The 2026 Asian Games are scheduled for Aichi-Nagoya, Japan, in September. Wrestling is one of India's strongest medal sports at the continental level, and selection trials are fiercely contested. Phogat, who competes in the 50 kg category, will face a field of younger challengers who have risen in her absence.

For the Indian diaspora, Phogat's story resonates beyond the mat. She was one of the faces of the wrestlers' protest movement in 2023, when athletes accused the then-federation chief of sexual harassment — a movement that drew global attention and led to significant changes in Indian sports governance.

Whether she makes the team or not, the Supreme Court has ensured she gets her chance. The larger question it raised — how much the judiciary should insert itself into sport — will linger far longer than any trial result.

*The Asian Games trials begin May 30 at the KD Jadhav Wrestling Hall in New Delhi.*""",
    "slug": "supreme-court-vinesh-phogat-asian-games-2026-trials-sports-judiciary-warning-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "image_url": vinesh_image,
    "image_attribution": "Wikimedia Commons" if vinesh_image and "wikimedia" in (vinesh_image or "").lower() else "Pexels",
    "sources": json.dumps([
        {"name": "Punjab Newsline", "url": "https://www.punjabnewsline.com/supreme-court-allows-vinesh-phogat-asian-games-2026-trials"},
        {"name": "Reuters", "url": "https://www.reuters.com/sports/"},
        {"name": "LiveLaw", "url": "https://www.livelaw.in/"}
    ])
})


# ------------------------------------------------------------------
# Article 2: India defense diplomacy at Shangri-La
# ------------------------------------------------------------------
print("\n=== Article 2: India at Shangri-La ===")
shangri_image = fetch_pexels_image("Singapore defense military meeting", "international diplomacy summit")
if shangri_image and not validate_image(shangri_image):
    shangri_image = None

articles.append({
    "headline": "India's Defence Secretary Held Five Bilateral Meetings in One Day at Shangri-La. Here Is What Each One Was About.",
    "subheadline": "Rajesh Kumar Singh met counterparts from the Netherlands, Australia, the EU, and key Indo-Pacific partners on the sidelines of Asia's biggest defense forum",
    "body": """India used the sidelines of the 2026 Shangri-La Dialogue in Singapore to run an intensive round of defense diplomacy, with Defence Secretary Rajesh Kumar Singh holding separate bilateral meetings with counterparts from the Netherlands, Australia, the European Union, and other Indo-Pacific partners on Saturday.

The engagements, announced by India's Ministry of Defence on X, underscored New Delhi's push to deepen military partnerships beyond its traditional strategic circle — at a moment when China's defence minister was conspicuously absent from the forum for the second consecutive year.

## Netherlands: Defence Industrial Collaboration

Singh's meeting with Dutch Defence Minister Dilan Yeşilgöz-Zegerius focused on expanding bilateral defence cooperation. Both sides discussed "strengthening military-to-military ties" and explored "opportunities for defence industrial collaboration," according to the defence ministry.

The India-Netherlands defence relationship has been growing quietly. The Netherlands is home to major defence technology firms, and India has been courting European partners as it diversifies its arms supply chains away from heavy dependence on Russia. Dutch expertise in naval systems, submarine technology, and cybersecurity aligns with India's modernisation priorities.

## Australia: Reviewing the Comprehensive Strategic Partnership

The Defence Secretary also met Australian Defence Secretary Meghan Quinn. The two reviewed progress under the India-Australia Comprehensive Strategic Partnership, assessed upcoming high-level exchanges, and identified new areas for deeper cooperation.

Australia and India have significantly expanded their defence relationship in recent years, particularly through the Quad framework and bilateral exercises like AUSINDEX and Malabar. Australian Deputy Prime Minister and Defence Minister Richard Marles, who is also at the Shangri-La Dialogue, is scheduled to visit India next — a sign of the accelerating tempo of engagement.

## EU: Military Interoperability

Singh held discussions with senior EU defence officials, focusing on military interoperability and defence industrial collaboration. The EU has been building its own defence identity independent of NATO, and India's interest in European defence technology — from fighter jets to secure communications — makes it a natural partner.

## India's Broader Indo-Pacific Pitch

Earlier on Friday, Singh had addressed think tanks and academics in Singapore on "India's Defence Diplomacy for a Stable, Secure and Inclusive Indo-Pacific." The session, attended by Indian High Commissioner to Singapore Shilpak Ambule, laid out New Delhi's vision for the region's security architecture.

The timing was deliberate. With US Defence Secretary Pete Hegseth using his keynote address to demand that Asian allies spend 3.5 percent of GDP on defence, India positioned itself as a partner that brings strategic depth without the transactional edge. New Delhi's defence spending hovers around 2.4 percent of GDP — high by Asian standards but below the threshold Hegseth laid out.

## China's Absence Amplified India's Presence

The biggest talking point at this year's dialogue was who was not there. Chinese Defence Minister Dong Jun skipped the forum for the second year running, sending only a delegation of PLA "experts and scholars." Even Hegseth took note: "I wish my counterpart was here at this conference."

Beijing's absence created a vacuum that India and other mid-tier powers were happy to fill. By running five bilateral meetings in a single day, Singh's team signaled that India sees itself as a hub in the Indo-Pacific security network — not just a spoke.

Zhou Bo, a retired PLA senior colonel attending as part of China's delegation, downplayed the absence but acknowledged the optics: "The level of the delegation is relatively low this time."

## What This Means for the Diaspora

India's expanding defence partnerships have implications beyond the military. Defence industrial collaboration often opens doors for technology transfer, joint ventures, and professional opportunities — areas where the Indian diaspora in Europe, Australia, and Southeast Asia is already deeply embedded. As India's defence economy grows toward its target of $25 billion in annual production, the commercial ecosystem around it will grow too.

*The Shangri-La Dialogue continues through May 31 in Singapore.*""",
    "slug": "india-defence-secretary-shangri-la-bilateral-netherlands-australia-eu-indo-pacific-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "image_url": shangri_image,
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "ANI / Daily Prabhat", "url": "https://www.dailyprabhat.com/india-expands-defence-diplomacy-with-netherlands-australia-and-eu-on-sidelines-of-shangri-la-dialogue/"},
        {"name": "NewKerala", "url": "https://www.newkerala.com/news/2026/india-indo-pacific-vision-shangri-la-dialogue.html"},
        {"name": "Reuters", "url": "https://www.reuters.com/world/asia-pacific/where-is-china-ask-delegates-asian-defence-forum-2026-05-30/"}
    ])
})


# ------------------------------------------------------------------
# Article 3: SEBI fines Suzlon Energy
# ------------------------------------------------------------------
print("\n=== Article 3: SEBI fines Suzlon ===")
suzlon_image = fetch_pexels_image("wind turbines India", "wind energy farm turbines")
if suzlon_image and not validate_image(suzlon_image):
    suzlon_image = None

articles.append({
    "headline": "SEBI Has Fined Suzlon Energy ₹15.95 Crore for Inflating Its Books. The Chairman and Vice-Chairman Got Personal Penalties Too.",
    "subheadline": "The markets regulator said Suzlon's disclosures 'created a false picture of financial strength' and misled investors through transactions with subsidiaries",
    "body": """India's Securities and Exchange Board of India on Friday imposed a penalty of ₹15.95 crore ($1.68 million) on Suzlon Energy for what it called serious lapses in the company's financial statements and disclosures — a ruling that adds to a difficult stretch for one of India's most prominent renewable energy companies.

SEBI did not stop at the corporate entity. The regulator also slapped personal monetary penalties on Suzlon's chairman and vice-chairman — ₹5.75 crore and ₹5.45 crore respectively — on charges that they were at the helm when the misreporting occurred.

## What SEBI Found

The order centers on Suzlon's transactions with its subsidiaries and associates. SEBI said these transactions resulted in the misstatement of financials and inflated the company's net worth, creating what the regulator described as "a false picture of financial strength affecting market integrity."

In plain terms: the disclosures Suzlon made to the stock exchanges about key material transactions did not reflect reality, and investors who relied on those disclosures to make decisions were misled.

Suzlon did not immediately respond to media requests for comment on the order.

## The Context: A Company That Has Reinvented Itself — Twice

The penalty lands at an awkward moment. Suzlon has spent the better part of a decade rehabilitating itself after a near-death experience. The company, once India's largest wind turbine manufacturer, defaulted on foreign currency convertible bonds in 2012 and spent years mired in debt restructuring, management upheaval, and shrinking market share.

By 2023, the tide appeared to turn. India's aggressive renewable energy targets — 500 GW of non-fossil fuel capacity by 2030 — gave Suzlon a tailwind. The company won large orders, posted its first profitable year in nearly a decade, and its stock price surged more than fivefold from its 2020 lows.

But the SEBI order reopens questions about the quality of the financial reporting that underpinned that recovery. If the disclosures during the period under review were unreliable, investors will want to know whether the more recent numbers can be trusted.

## A Pattern of Regulatory Scrutiny

SEBI's action against Suzlon is part of a broader wave of enforcement. On the same day, the regulator also disposed of a long-running disclosure case against NDTV, ruling that the broadcaster had not violated any rules — a contrasting outcome that highlights the case-by-case nature of securities enforcement.

The Suzlon order is also notable for targeting individual executives. Indian securities law gives SEBI broad powers to impose personal liability on directors and officers who presided over financial irregularities, but the regulator has traditionally been cautious about using this power. Naming the chairman and vice-chairman sends a signal that passive oversight is not a defense.

## What It Means for India's Green Energy Push

Suzlon operates in a sector that India desperately needs to succeed. The country has committed to having 50 percent of its energy come from renewable sources by 2030, and wind energy is a critical part of that equation. India's installed wind capacity stands at roughly 47 GW, but the government wants to reach 140 GW by the end of the decade.

To get there, India needs companies like Suzlon to be credible counterparties for banks, international investors, and development finance institutions. A SEBI enforcement action for financial misreporting — particularly one that questions the integrity of subsidiary transactions — could complicate Suzlon's access to capital at exactly the moment it needs to scale.

For NRI investors who have bet on India's green transition, the order is a reminder that corporate governance risk remains a live variable. India's renewable energy story is real, but the companies driving it are not immune to the accounting and governance issues that have plagued Indian corporates across sectors.

## The Numbers

The total penalty across the company and its executives comes to ₹27.15 crore — not a crippling sum for a company with a market capitalisation of over ₹70,000 crore, but significant as a regulatory marker. SEBI's order also opens the door for civil suits from investors who can demonstrate they relied on the misleading disclosures to their detriment.

Suzlon's stock closed flat on Friday, suggesting the market had either priced in the risk or had not yet fully digested the implications. Monday's trading session will be the real test.

*SEBI's full order is available on its website at sebi.gov.in.*""",
    "slug": "sebi-fines-suzlon-energy-15-crore-financial-misreporting-chairman-penalty-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "image_url": suzlon_image,
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/business/finance/india-markets-regulator-fines-suzlon-energy-17-million-lapses-financial-2026-05-30/"},
        {"name": "SEBI Order", "url": "https://www.sebi.gov.in/enforcement/orders.html"}
    ])
})


# ------------------------------------------------------------------
# Article 4: Newark Delaney Hall standoff — immigration climate
# ------------------------------------------------------------------
print("\n=== Article 4: Newark Delaney Hall ===")
newark_image = fetch_pexels_image("protest demonstration police barrier", "immigration protest United States")
if newark_image and not validate_image(newark_image):
    newark_image = None

articles.append({
    "headline": "A Weeklong Standoff at a Newark Detention Center Is Rewriting the Rules of Immigration Enforcement. Legal Immigrants Are Watching.",
    "subheadline": "New Jersey's governor ordered state police to create protest zones outside Delaney Hall as dueling demonstrations, pepper spray, and an FBI arrest intensified the confrontation",
    "body": """What began as a hunger strike by detained immigrants at a private facility in Newark, New Jersey, has escalated into one of the most significant confrontations between state and federal authorities over immigration enforcement in the Trump era — with implications that extend far beyond the undocumented population it directly affects.

## The Basics

Delaney Hall is a 1,000-bed detention center in Newark operated by the GEO Group, a private prison company, on behalf of U.S. Immigration and Customs Enforcement. On May 22, detainees launched a hunger and labour strike, alleging inadequate medical care, insufficient food, and detention without due process. They published an open letter detailing their grievances.

The Department of Homeland Security has denied the allegations, calling the facility well-maintained and properly audited.

But the situation outside the facility has become its own crisis. Protesters began gathering in large numbers, confrontations with ICE agents turned physical, pepper spray was deployed, and a protester's foot was reportedly caught under a truck wheel. The FBI arrested one individual for allegedly threatening to kill an ICE officer's family.

## The Governor Steps In

On Friday, New Jersey Governor Mikie Sherrill ordered state police to assume control of the area outside Delaney Hall. State troopers set up "protected protest zones" and vehicle checkpoints, while ICE agents agreed to withdraw from the immediate perimeter.

"We've seen increasing violence, arrests, and pepper spray at Delaney Hall, as well as public threats from the Trump administration," Sherrill said. "It has grown unsafe and that is completely unacceptable."

Sherrill explicitly invoked the spectre of fatal outcomes: "We know what ICE has done in other states and that American citizens have lost their lives." She reiterated her demand to close the facility entirely.

DHS Secretary Markwayne Mullin pushed back. "All detainees are provided with proper meals, quality water, blankets, medical treatment, and have opportunities to communicate with their family members and lawyers," he posted on X.

## Dueling Protests Expected

Saturday is expected to be the most volatile day yet. Both pro-ICE and anti-ICE demonstrators have announced rallies outside the facility. State police have established separate assembly zones for each group.

The pro-ICE rally gained momentum after former Border Patrol commander-at-large Gregory Bovino arrived in Newark on Thursday, telling ICE agents to "hang in there." Bovino retired in March after controversy over his approach to immigration enforcement.

## Why Legal Immigrants Should Care

The Delaney Hall standoff is not directly about legal immigration. The detainees are individuals held on immigration violations, not H-1B workers or green card holders. But the broader dynamics it illustrates — the expansion of ICE operations, the use of private detention facilities, the political weaponisation of immigration enforcement — shape the environment every immigrant in America inhabits.

When ICE operations intensify, the knock-on effects ripple outward. Workplace raids increase scrutiny on all foreign-born employees. Political rhetoric around immigration hardens. And administrative decisions — visa processing speeds, green card adjudications, naturalization timelines — are made within an ecosystem influenced by enforcement priorities.

For the Indian diaspora specifically, the picture is complex. NRIs on H-1B and L-1 visas are legally present, but the hostile immigration climate creates anxiety about interactions with federal authorities, complicates travel, and affects the willingness of employers to sponsor future visas. With 142,000 tech jobs already cut in 2026 and each layoff starting a 60-day deportation clock for visa holders, the gap between "legal" and "secure" has never felt wider.

## The Larger Pattern

Delaney Hall is not an isolated incident. It sits within a pattern that includes the Texas SB4 law (now enforceable, allowing state-level arrests and deportation orders), the $100,000 H-1B fee whose legality a federal judge questioned just this week, and DHS threats to shut down international flights at Newark Airport over the city's sanctuary policies.

Each of these developments is distinct. Together, they describe a federal approach to immigration that is simultaneously expanding enforcement powers, raising barriers to legal entry, and creating confrontations with state and local authorities who resist.

The detainees at Delaney Hall are at the sharp end of this system. But everyone navigating American immigration — from an undocumented worker in Newark to an Indian software engineer in San Jose renewing their H-1B — is operating within its gravitational field.

*A Saturday rally outside Delaney Hall is scheduled for 11 AM EST. State police will maintain a presence through the weekend.*""",
    "slug": "newark-delaney-hall-ice-detention-standoff-nj-state-police-immigration-enforcement-nri-20260530",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "image_url": newark_image,
    "image_attribution": "Pexels",
    "sources": json.dumps([
        {"name": "Reuters", "url": "https://www.reuters.com/world/us/new-jersey-state-police-assert-control-outside-migrant-detention-center-2026-05-30/"},
        {"name": "CNN", "url": "https://www.cnn.com/2026/05/30/us/newark-delaney-hall-detention-center-protests/"},
        {"name": "NorthJersey.com", "url": "https://www.northjersey.com/story/news/new-jersey/2026/05/30/sherrill-nj-state-police-delaney-hall/"}
    ])
})


# ============================================================
# PUBLISH
# ============================================================
print("\n=== Publishing articles ===")
success_count = 0
for i, article in enumerate(articles, 1):
    print(f"\nArticle {i}: {article['headline'][:60]}...")
    if not article.get("image_url"):
        print("  ⚠ No image found — publishing without image")
    result = publish_article(article)
    if result:
        success_count += 1

print(f"\n=== Done: {success_count}/{len(articles)} articles published ===")
