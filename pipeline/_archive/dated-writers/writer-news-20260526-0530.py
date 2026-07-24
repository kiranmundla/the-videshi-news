#!/usr/bin/env python3
"""Videshi Writer — 2 fresh NEWS articles for 2026-05-26 ~05:30 PDT batch
Topics: 1) Trump demands Muslim nations join Abraham Accords as condition of Iran deal — Pakistan, Saudi Arabia reject
        2) Iran's Supreme Leader reportedly agrees to surrender uranium — but IRGC threatens retaliation after US strikes
"""

import json, os, uuid, re, requests, subprocess, urllib.parse
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

def make_slug(slug_base, date_suffix="20260526"):
    slug = slug_base.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'\s+', '-', slug.strip())
    slug = slug[:70].rstrip('-')
    return f"{slug}-{date_suffix}"

# ── Wikipedia person image (MANDATORY for person articles) ──
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    encoded = urllib.parse.quote(person_name.replace(' ', '_'))
    try:
        r = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{encoded}",
            headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"},
            timeout=10
        )
        if r.status_code == 200:
            data = r.json()
            img = data.get("originalimage", {}).get("source") or data.get("thumbnail", {}).get("source")
            if img:
                print(f"  ✓ Wikipedia image found for '{person_name}': {img[:80]}...")
                return img
    except Exception as e:
        print(f"  ⚠ Wikipedia API error for '{person_name}': {e}")
    return None

# ── Pexels helper ──
pexels_env = Path.home() / "workspace" / ".env.pexels"
PEXELS_KEY = None
if pexels_env.exists():
    for line in pexels_env.read_text().strip().splitlines():
        if line.startswith("PEXELS_API_KEY="):
            PEXELS_KEY = line.split("=", 1)[1].strip()

def fetch_pexels_image(query, fallback_query=None):
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
    return image_url

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
# ARTICLE 1: Trump Demands Muslim Nations Join Abraham Accords
#   — Pakistan and Saudi Arabia Reject; India Watches
# ══════════════════════════════════════════════════════════════

slug1 = make_slug("trump-abraham-accords-mandatory-pakistan-saudi-reject-iran-deal")
headline1_prefix = "trump"
alt_checks1 = ["abraham accords", "pakistan", "mandatory"]
if slug1 not in existing_slugs and not any(all(kw in h for kw in ["abraham", "accords"]) for h in existing_headlines_lower):
    body1 = """On Monday, between announcing that the Iran deal was "largely negotiated" and watching his military sink two IRGC boats in the Strait of Hormuz, President Donald Trump posted a demand on Truth Social that would, if taken literally, redraw the diplomatic map of the Muslim world.

"I am mandatorily requesting that all Countries immediately sign the Abraham Accords," Trump wrote. He named Saudi Arabia, Qatar, Pakistan, Turkey, Egypt, and Jordan. He then added that if Iran signs its agreement with the United States, "it would be an Honor to have them also be part of this unparalleled World Coalition."

The word "mandatorily" is not a recognized diplomatic term. But Trump's intent was clear: he wants the Iran peace deal — which would reopen the Strait of Hormuz, end the three-month naval war, and begin negotiations over Iran's nuclear programme — to be embedded within a broader normalisation of relations between Muslim-majority nations and Israel.

Pakistan said no within hours.

Saudi Arabia, according to multiple reports, has signalled that it will not sign without a Palestinian state — the same condition it has maintained since the original Abraham Accords were signed in 2020 by the UAE and Bahrain.

Turkey has not responded publicly. Egypt and Jordan already have peace treaties with Israel dating back decades and are, in Trump's framing, already honorary members.

## What the Abraham Accords Actually Are

The Abraham Accords were brokered during Trump's first term in 2020. The United Arab Emirates and Bahrain signed normalisation agreements with Israel. Morocco and Sudan followed. The deals were transactional: the UAE got F-35 fighter jets, Morocco got U.S. recognition of its sovereignty over Western Sahara, Sudan got removed from the state sponsors of terrorism list, and Israel got diplomatic recognition from four Arab states without conceding anything on Palestine.

The accords were Trump's signature foreign policy achievement. He has spent his second term trying to expand them — first through a Saudi deal that collapsed over Gaza in 2023, and now through the Iran war, which has created new leverage.

The logic is simple: if Trump can end the Iran war and reopen the Strait of Hormuz — restoring 20 percent of global oil and gas supply — he can demand that the countries benefiting from that restoration reciprocate by normalising relations with Israel. The Strait is the lever. The accords are the price.

## Why Pakistan Said No

Pakistan's rejection was immediate and categorical. The foreign ministry said Pakistan's position on Israel "remains unchanged" and is tied to the resolution of the Palestinian issue. Behind the diplomatic language is a domestic political reality: no Pakistani government could survive recognising Israel. The issue carries religious, ideological, and popular weight that no amount of American pressure can override.

But Pakistan's role in the Iran deal is more complicated than its rejection of the accords suggests. The deal framework was brokered in part through Pakistani channels. Iran's foreign minister Abbas Araghchi was in Islamabad when the deal's terms were being discussed. Pakistan — which shares a 959-kilometre border with Iran and has its own Balochistan insurgency that crosses that border — has a direct interest in a stable, non-nuclear Iran.

Pakistan is willing to help mediate the Iran deal. It is not willing to recognise Israel as the price of that mediation. Trump's conflation of the two may have undermined the very channel he needs.

## Why Saudi Arabia Won't Sign — Yet

Saudi Arabia has been the great white whale of the Abraham Accords since 2020. A Saudi-Israel normalisation deal would transform the Middle East — and Trump knows it.

Crown Prince Mohammed bin Salman reportedly came close to signing in 2023 before the Gaza war made it politically impossible. The condition has always been the same: a credible, irreversible path to a Palestinian state.

Trump's Truth Social post — demanding that Saudi Arabia sign the accords immediately and linking them to the Iran deal — is a negotiating gambit, not a final position. But it reveals the scale of his ambition: he wants a single grand bargain that ends the Iran war, reopens Hormuz, expands the Abraham Accords to a dozen countries, and resolves (or at least appears to resolve) the Palestinian question, all before the November midterms.

The Saudi response, through diplomatic channels, has been that the accords are "under consideration" but cannot be decoupled from Palestine. Translation: we are interested, but not at this price, and not on this timeline.

## What This Means for India

India is not on Trump's list. India does not need to sign the Abraham Accords because India already has full diplomatic relations with Israel — relations that have deepened dramatically under Modi, encompassing defence procurement, intelligence sharing, agricultural technology, and cyber cooperation.

But India is affected by every dimension of Trump's gambit.

If the Abraham Accords expand to include Saudi Arabia, it consolidates a U.S.-Israel-Gulf axis that India has carefully navigated without joining. India has maintained simultaneous relationships with Israel, Saudi Arabia, Iran, and the UAE — a diplomatic balancing act that has served it well. An expanded accords framework that pulls Saudi Arabia and potentially Turkey into formal alignment with Israel would pressure India to pick sides more explicitly than it has been willing to.

If Pakistan's rejection of the accords strains its relationship with the U.S. further — on top of the existing tensions over Pakistan's China dependency, its Taliban relationship, and its nuclear programme — it could push Pakistan closer to China and Iran, creating a triangle that India's security planners have been warning about for years.

And if the Iran deal itself is jeopardised by Trump's insistence on tying it to the accords — which Pakistan, Saudi Arabia, and Turkey have all signalled they will not accept — then the Strait of Hormuz stays closed, oil stays at $98, the rupee stays weak, and India's fuel price hikes continue.

India's External Affairs Minister Jaishankar, who met Rubio in New Delhi on the same day Trump posted his Abraham Accords demand, conspicuously did not mention the accords in his press conference. He talked about critical minerals, maritime surveillance, and "full-spectrum regional architecture." The omission was deliberate.

## What NRIs Are Watching

For the Indian diaspora, Trump's Abraham Accords push intersects with their lives in three ways.

First, the Gulf connection. Over 8.5 million Indians live and work in the Gulf states — the UAE, Saudi Arabia, Qatar, Kuwait, Oman, and Bahrain. These countries are the backbone of India's remittance economy. Any diplomatic upheaval in the Gulf — whether from the Iran war, the Abraham Accords, or the intersection of both — affects the stability, visa policies, and economic environment of the countries where millions of Indians earn their livelihoods.

Second, the Pakistan factor. The Indian diaspora watches Pakistan's geopolitical moves with the attention that comes from shared history, family ties that cross borders, and a security relationship that shapes both countries' foreign policies. Pakistan rejecting the Abraham Accords while mediating the Iran deal creates a complex dynamic that affects India-Pakistan relations, Kashmir diplomacy, and the broader question of South Asia's place in the Middle Eastern order.

Third, the oil price. Every dimension of Trump's gambit — the accords, the Iran deal, the Strait of Hormuz — ultimately flows back to the barrel price that determines the rupee, the inflation rate, and the cost of living for 1.4 billion people. If Trump's maximalist demands delay or derail the Iran deal, the NRI community pays the price in weaker remittance value and higher costs for families back home.

Trump wants a grand bargain. The Muslim world is offering à la carte. The gap between the two is where the price of oil — and the Indian rupee — will be set for the rest of 2026."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Trump Just Demanded That Every Muslim Nation Join the Abraham Accords as Part of the Iran Deal. Pakistan Said No. Saudi Arabia Said Not Without Palestine. The Grand Bargain That Could Set the Oil Price for the Rest of 2026.",
        "subheadline": "In a Truth Social post between announcing the Iran deal was 'largely negotiated' and watching his military sink two IRGC boats, Trump 'mandatorily requested' that Saudi Arabia, Pakistan, Qatar, Turkey, Egypt, and Jordan immediately sign the Abraham Accords — and suggested Iran itself could join. Pakistan rejected within hours. Saudi Arabia repeated its demand for a Palestinian state. India, which has full Israel relations but carefully balances the Gulf, was conspicuously absent from Trump's list and Jaishankar's press conference. If the accords demand delays the Iran deal, the Strait stays closed, oil stays at $98, and the rupee stays weak.",
        "slug": slug1,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The Abraham Accords push affects the Indian diaspora through three channels: the 8.5 million Indians in the Gulf whose stability depends on the region's diplomatic order; the Pakistan dynamic that shapes India-Pakistan relations and Kashmir diplomacy; and the oil price that determines the rupee and the cost of living for families back home. Trump wants a grand bargain. The Muslim world is offering à la carte. The gap between the two is where the rupee will trade for the rest of 2026.",
        "tags": ["Abraham Accords", "Trump", "Pakistan", "Saudi Arabia", "Israel", "Iran deal", "Strait of Hormuz", "oil prices", "India", "Jaishankar", "Gulf states", "NRI", "Middle East", "diplomacy", "normalisation"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "Reuters — Trump links Abraham Accords to any Iran deal", "url": "https://www.reuters.com/world/trump-links-abraham-accords-any-iran-deal-2026-05-26/"},
            {"name": "Global Banking & Finance — Trump Connects Abraham Accords to Iran Deal in Middle East Push", "url": "https://www.globalbankingandfinance.com/news/trump-connects-abraham-accords-iran-deal-middle-east-push/"},
            {"name": "Washington Examiner — Despite Trump's upbeat pronouncements, peace does not appear to be at hand", "url": "https://www.washingtonexaminer.com/policy/defense/despite-trumps-upbeat-iran-deal-peace/"},
            {"name": "New York Post — Iran's supreme leader has agreed 'in principle' to give up uranium", "url": "https://nypost.com/2026/05/25/iran-supreme-leader-agreed-uranium-peace-deal/"},
            {"name": "LatestLY — What Are the Abraham Accords? How Trump Is Using the 2020 Peace Pacts To End the Iran War", "url": "https://www.latestly.com/agency-news/what-are-abraham-accords-trump-iran-war-2026.html"}
        ]),
        "score_total": 87,
        "status": "published",
        "published_at": now_iso,
        "body": body1
    })
    print(f"✓ Article 1 prepared: Trump / Abraham Accords / Pakistan rejects / Saudi Arabia / India angle")
else:
    print(f"✗ Article 1 skipped (duplicate detected)")


# ══════════════════════════════════════════════════════════════
# ARTICLE 2: Iran's Supreme Leader Reportedly Agrees to Surrender Uranium
#   — But IRGC Claims Downing of US Drone, Threatens Retaliation
# ══════════════════════════════════════════════════════════════

slug2 = make_slug("iran-supreme-leader-uranium-surrender-irgc-drone-retaliation")
headline2_prefix = "iran"
alt_checks2 = ["uranium", "supreme leader"]
if slug2 not in existing_slugs and not any(all(kw in h for kw in ["uranium", "iran"]) for h in existing_headlines_lower):
    body2 = """On Saturday, a senior Trump administration official told the New York Post that Iran's Supreme Leader had agreed "in principle" to give up the country's stockpile of highly enriched uranium as part of a deal to end the war with the United States.

"We feel quite confident that the supreme leader has signed off on the broad template," the official said.

On Monday, Iran's Islamic Revolutionary Guard Corps said it had shot down a U.S. MQ-9 Reaper surveillance drone over the Persian Gulf, engaged a U.S. F-35 fighter jet that entered Iranian airspace, and reserved "the right of reciprocal response" — meaning retaliation — after the United States sank two IRGC boats and destroyed a missile site near Bandar Abbas.

Four Iranian personnel were killed in the U.S. strikes on the boats.

Both statements are true. Both are happening simultaneously. This is the Iran deal in May 2026: a peace being negotiated by diplomats and a war being fought by militaries, running on parallel tracks that could converge into a historic agreement or collide into a catastrophic escalation.

## The Deal Architecture

The framework that has emerged from weeks of negotiations — brokered in part through Pakistani channels — has two steps, according to multiple U.S. officials:

**Step 1:** Iran reopens the Strait of Hormuz without tolls. Iran clears the mines its forces have laid in the strait. The U.S. lifts its naval blockade. A 60-day ceasefire extension begins. During this period, Iran surrenders its stockpile of highly enriched uranium — material that could, if further processed, be used to build a nuclear weapon.

**Step 2:** After the uranium is extracted — Trump officials call it removing the "nuclear dust" — sanctions relief begins. This includes unfreezing Iranian assets, lifting oil export restrictions, and restoring Iran's access to the global financial system. An enforcement mechanism bars future enrichment.

The phrase "no dust, no dollars" has become the administration's internal shorthand. Iran gets nothing until the uranium is physically out of the country.

Iran's position, as described by the U.S. official, involves "national pride considerations" for how the material is offloaded. Translation: Iran will not be seen to be surrendering its nuclear programme under American military pressure. The optics matter as much as the substance. The mechanism for extraction — who takes custody, where it goes, how it is verified — is where the remaining negotiations will focus.

## The IRGC Problem

The single biggest obstacle to the deal is not the diplomatic framework. It is the Islamic Revolutionary Guard Corps.

The IRGC operates with substantial independence from Iran's civilian government and foreign ministry. It controls its own military forces, its own intelligence apparatus, its own economic empire, and its own strategic doctrine. When Iran's foreign minister Abbas Araghchi negotiates in Doha or Islamabad, he speaks for the Iranian government. He does not necessarily speak for the IRGC.

The boats laying mines in the Strait of Hormuz on Monday were IRGC boats. The surface-to-air missiles fired at U.S. warplanes were IRGC missiles. The claim that a U.S. MQ-9 Reaper drone was shot down came from the IRGC's public affairs office. The threat of retaliation — "the right of reciprocal response is legitimate and definite" — was an IRGC statement, not a foreign ministry statement.

This distinction matters because a peace deal signed by Iran's government must be implemented by Iran's military — and the IRGC is Iran's most powerful military force. If the IRGC does not accept the deal's terms, it can sabotage implementation through continued mine-laying, drone interdiction, or proxy attacks across the region.

The Wall Street Journal reported that the IRGC claimed its air defence units had "identified and engaged U.S. drones and a F-35 jet fighter which entered Iranian airspace in the Persian Gulf area." Fox News's Jennifer Griffin, citing U.S. officials, said the Iranian missile sites were destroyed because they were targeting U.S. warplanes, and that "military action is over for the moment, and the ceasefire is still in effect."

The ceasefire is still in effect. Four IRGC personnel are dead. A U.S. drone may have been shot down. Both sides call it self-defence. This is what passes for peace in the Strait of Hormuz in 2026.

## The Uranium Question

Iran's nuclear programme has been the central security concern of the Middle East for two decades. Under the 2015 JCPOA (the Obama-era deal that Trump withdrew from in 2018), Iran agreed to limit its enrichment to 3.67 percent — far below the 90 percent needed for a weapon. After the U.S. withdrawal, Iran began enriching to 20 percent, then 60 percent, and has accumulated enough material that the International Atomic Energy Agency has repeatedly warned it could produce weapons-grade uranium within weeks if it chose to.

The current deal would require Iran to surrender this stockpile entirely. It is a demand far more aggressive than anything in the JCPOA, which merely capped enrichment levels. If Iran complies, it would be the most significant nuclear disarmament event since South Africa voluntarily dismantled its weapons in the early 1990s.

The "in principle" agreement from the Supreme Leader suggests that Iran's leadership has accepted the strategic logic: surrender the uranium, get the sanctions lifted, reopen oil exports, rejoin the global economy. The alternative — continued war, a closed strait, $100 oil that Iran cannot sell, and an economy under unprecedented pressure — is worse.

But "in principle" is not "signed." The gap between the two is where deals die. And the IRGC — which has spent three months laying mines, firing missiles, and building martyrdom narratives around the four personnel killed on Monday — may not share the Supreme Leader's calculus.

## What India Is Calculating

India's interest in this deal is existential in economic terms.

If the deal holds and the Strait reopens, oil prices drop. Goldman Sachs has modelled Brent crude at $72-78 per barrel in a full-reopening scenario — down from today's $98. That would cut India's oil import bill by approximately $35 billion annually. The rupee would strengthen. The RBI would not need to raise rates. Fuel prices would stabilise or fall. Inflation would ease. The cascading effect through transportation, food supply chains, and consumer spending would be the single largest positive economic shock India has experienced since the pandemic recovery.

If the deal collapses — because of IRGC sabotage, because Trump's Abraham Accords demand proves to be a dealbreaker, or because the uranium extraction mechanism cannot be agreed — oil stays above $95. India's balance of payments deficit widens. The rupee, already down 4.7 percent against the dollar since the war began, falls further. The RBI raises rates. Growth slows.

India has no influence over the negotiations. It cannot pressure the IRGC. It cannot convince Trump to decouple the Abraham Accords from the Iran deal. It cannot make the uranium extraction happen faster. All it can do is watch, hedge, and prepare for both outcomes.

The Quad meeting in New Delhi on Monday — where Jaishankar and Rubio signed the critical minerals framework — was, in part, India's hedge. If the Strait stays closed and Gulf oil remains unreliable, India needs alternative supply chains, alternative energy sources, and alternative economic partnerships. The rare earths deal, the maritime surveillance initiative, and the Fiji port project are all pieces of an India that is preparing for a world where the old oil routes may not reopen.

## What NRIs Are Watching

The uranium question is not abstract for the Indian diaspora. It determines whether the next six months bring economic relief or economic pain.

If Iran surrenders its uranium and the deal holds, the NRI financial equation improves across every variable: oil down, rupee up, inflation eases, remittance value increases, Indian equity markets rally, and the RBI pauses or cuts rates. The 18 million-strong diaspora, sending over $125 billion annually, would see every dollar stretch further at the receiving end.

If the deal falls apart, every variable reverses. Oil up, rupee down, inflation accelerates, fuel prices rise again, and the RBI tightens. The cost of living for families in India — which has already risen sharply since the Iran war began — continues to climb.

The deal is closer than it has ever been. Iran's Supreme Leader has reportedly agreed in principle to the single most significant concession. The 60-day framework exists. The terms are specific. The intent appears genuine on both sides.

But the IRGC is laying mines. The U.S. is sinking boats. A drone may have been shot down. Four people are dead. The word "ceasefire" means something different in the Strait of Hormuz than it does anywhere else on earth.

The next few days will determine whether the deal moves from "in principle" to "signed" — or whether the parallel tracks of diplomacy and war finally collide."""

    articles.append({
        "id": str(uuid.uuid4()),
        "headline": "Iran's Supreme Leader Has Reportedly Agreed to Surrender the Country's Enriched Uranium. The IRGC Says It Shot Down a US Drone and Reserves the Right to Retaliate. Both Things Are Happening at the Same Time.",
        "subheadline": "A senior Trump official said the Supreme Leader has 'signed off on the broad template' — Iran reopens the Strait of Hormuz, clears mines, surrenders highly enriched uranium, and the U.S. lifts sanctions. 'No dust, no dollars.' But the IRGC claimed it downed a U.S. MQ-9 Reaper drone, engaged an F-35, and warned of retaliation after four IRGC personnel were killed in Monday's U.S. strikes near Bandar Abbas. The deal's architecture exists. The diplomatic intent appears genuine. The military reality on the water is running on a parallel track. India's entire economic outlook for the next six months — oil price, rupee, inflation, RBI rates — depends on which track wins.",
        "slug": slug2,
        "category": "news",
        "vertical": "nri-world",
        "diaspora_angle": "The uranium deal is the single variable that determines the NRI financial equation for the rest of 2026. Deal holds: oil drops to $72-78, rupee strengthens, inflation eases, remittance value increases, RBI pauses. Deal collapses: oil stays above $95, rupee falls further, inflation accelerates, RBI raises rates, cost of living keeps climbing. The 18 million diaspora sending $125 billion annually is watching the gap between 'in principle' and 'signed' — because that gap is where the rupee will trade.",
        "tags": ["Iran", "uranium", "nuclear deal", "IRGC", "Supreme Leader", "MQ-9 Reaper", "F-35", "Strait of Hormuz", "Bandar Abbas", "ceasefire", "oil prices", "India", "rupee", "RBI", "Goldman Sachs", "NRI", "remittances", "Trump", "JCPOA"],
        "urgency": "high",
        "sources": json.dumps([
            {"name": "New York Post — Iran's supreme leader has agreed 'in principle' to give up uranium as part of peace deal, US official says", "url": "https://nypost.com/2026/05/25/iran-supreme-leader-agreed-uranium-peace-deal/"},
            {"name": "Wall Street Journal — Iran Warns U.S. It Will Retaliate Against Cease-Fire Violations", "url": "https://www.wsj.com/world/middle-east/iran-warns-us-retaliate-ceasefire-violations-2026/"},
            {"name": "Washington Examiner — Despite Trump's upbeat pronouncements, peace does not appear to be at hand", "url": "https://www.washingtonexaminer.com/policy/defense/despite-trumps-upbeat-iran-deal-peace/"},
            {"name": "Washington Examiner — US launches 'self-defense strikes' in Iran as peace negotiations continue", "url": "https://www.washingtonexaminer.com/policy/defense/us-self-defense-strikes-iran/"},
            {"name": "Reuters — Iran says new US strikes violated ceasefire", "url": "https://www.reuters.com/world/iran-says-new-us-strikes-violated-ceasefire-2026-05-27/"}
        ]),
        "score_total": 89,
        "status": "published",
        "published_at": now_plus1,
        "body": body2
    })
    print(f"✓ Article 2 prepared: Iran uranium deal / IRGC retaliation / drone downed / India calculus")
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

    try:
        result = sb_post("p2_articles", art)
        print(f"  ✓ Inserted: {art_id}")
    except Exception as e:
        print(f"  ✗ Insert failed: {e}")
        continue

    # Image sourcing — Wikipedia first for person articles, Pexels fallback
    img_url = None
    img_attribution = "The Videshi"

    if i == 0:
        # Abraham Accords / Trump — Trump is central figure
        img_url = fetch_wikipedia_person_image("Donald Trump")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            img_url = fetch_pexels_image("Abraham Accords Middle East diplomacy", "diplomatic summit flags Middle East")
    elif i == 1:
        # Iran uranium deal / IRGC — try Ali Khamenei (Supreme Leader), then Strait of Hormuz
        img_url = fetch_wikipedia_person_image("Ali Khamenei")
        if img_url:
            img_attribution = "Wikimedia Commons"
        else:
            img_url = fetch_wikipedia_person_image("Supreme Leader of Iran")
            if img_url:
                img_attribution = "Wikimedia Commons"
            else:
                img_url = fetch_pexels_image("Strait of Hormuz warship naval", "Iran military")

    if img_url:
        filename = f"{art['slug']}.jpg"
        final_url = upload_image_to_supabase(img_url, filename)
        try:
            sb_patch("p2_articles", {"id": f"eq.{art_id}"}, {
                "image_url": final_url,
                "image_attribution": img_attribution
            })
            print(f"  ✓ Image linked (attribution: {img_attribution})")
        except Exception as e:
            print(f"  ⚠ Image PATCH failed: {e}")

# ══════════════════════════════════════════════════════════════
# SCORE DECAY
# ══════════════════════════════════════════════════════════════

print("\n📉 Applying score decay to older news articles...")
try:
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

    mid_arts = sb_get("p2_articles", {
        "select": "id,score_total",
        "status": "eq.published",
        "category": "eq.news",
        "published_at": f"lt.{(now - timedelta(days=3)).isoformat().replace('+00:00', 'Z')}",
        "score_total": "gt.50",
        "limit": "200"
    })
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
        ["git", "commit", "-m", f"news: Trump Abraham Accords push + Iran uranium deal ({now.strftime('%Y-%m-%d %H:%M')} UTC)"],
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
