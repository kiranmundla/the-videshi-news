#!/usr/bin/env python3
"""
The Videshi News Writer — 2026-05-29 batch
Publishes 3 news articles with Wikipedia/Pexels images.
"""

import json, os, sys, time, uuid, re
import requests
from datetime import datetime, timezone

# ─── ENV ────────────────────────────────────────────────────────────
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
PEXELS_API_KEY = os.environ.get("PEXELS_API_KEY", "")

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# ─── IMAGE HELPERS ──────────────────────────────────────────────────
def fetch_wikipedia_person_image(person_name):
    """Fetch a person's actual photo from Wikipedia. Returns image URL or None."""
    import urllib.parse
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


def fetch_pexels_image(query, fallback_query=None):
    """Fetch a relevant image from Pexels. Returns URL or None."""
    if not PEXELS_API_KEY:
        print("  ⚠ No Pexels API key")
        return None
    for q in [query, fallback_query]:
        if not q:
            continue
        try:
            import subprocess
            result = subprocess.run(
                ["curl", "-sS", "-H", f"Authorization: {PEXELS_API_KEY}",
                 f"https://api.pexels.com/v1/search?query={requests.utils.quote(q)}&per_page=5&orientation=landscape"],
                capture_output=True, text=True, timeout=15
            )
            data = json.loads(result.stdout)
            photos = data.get("photos", [])
            for photo in photos:
                url = photo.get("src", {}).get("large2x") or photo.get("src", {}).get("original")
                if url:
                    print(f"  ✓ Pexels image found for '{q}': {url[:80]}...")
                    return url
        except Exception as e:
            print(f"  ⚠ Pexels error for '{q}': {e}")
    return None


def upload_image_to_supabase(image_url, filename):
    """Download an image and upload to Supabase storage. Returns public URL."""
    try:
        r = requests.get(image_url, headers={"User-Agent": "TheVideshi/1.0 (thevideshi.com)"}, timeout=15)
        if r.status_code != 200:
            print(f"  ⚠ Failed to download image: HTTP {r.status_code}")
            return image_url  # fallback to original
        content_type = r.headers.get("Content-Type", "image/jpeg")
        if "image" not in content_type:
            print(f"  ⚠ Not an image: {content_type}")
            return image_url
        if len(r.content) < 5000:
            print(f"  ⚠ Image too small: {len(r.content)} bytes")
            return image_url

        # Upload to Supabase storage
        upload_url = f"{SUPABASE_URL}/storage/v1/object/article-images/{filename}"
        resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type": content_type,
                "x-upsert": "true",
            },
            data=r.content,
            timeout=30,
        )
        if resp.status_code in (200, 201):
            public_url = f"{SUPABASE_URL}/storage/v1/object/public/article-images/{filename}"
            print(f"  ✓ Uploaded to Supabase: {public_url[:80]}...")
            return public_url
        else:
            print(f"  ⚠ Supabase upload failed: {resp.status_code} {resp.text[:200]}")
            return image_url
    except Exception as e:
        print(f"  ⚠ Upload error: {e}")
        return image_url


def validate_image(url):
    """Check if an image URL is valid and not a tiny placeholder."""
    if not url:
        return False
    # Block Meta CDN URLs
    bad_domains = ["fbcdn.net", "cdninstagram.com", "lookaside.fbsbx.com"]
    bad_params = ["_nc_ht=", "_nc_cat=", "ccb="]
    for bd in bad_domains:
        if bd in url:
            return False
    for bp in bad_params:
        if bp in url:
            return False
    try:
        r = requests.head(url, headers={"User-Agent": "TheVideshi/1.0"}, timeout=10, allow_redirects=True)
        ct = r.headers.get("Content-Type", "")
        cl = int(r.headers.get("Content-Length", 0))
        if "image" not in ct:
            return False
        if cl > 0 and cl < 5000:
            return False
        return r.status_code == 200
    except:
        return True  # can't verify, assume OK


# ─── ARTICLE PUBLISHER ─────────────────────────────────────────────
def publish_article(article):
    """Insert article into Supabase."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    payload = {
        "headline": article["headline"],
        "subheadline": article["subheadline"],
        "body": article["body"],
        "slug": article["slug"],
        "category": article["category"],
        "vertical": article.get("vertical", "news"),
        "status": "published",
        "published_at": now,
        "sources": json.dumps(article.get("sources", [])),
        "image_url": article.get("image_url"),
        "image_caption": article.get("image_caption", ""),
        "image_attribution": article.get("image_attribution", ""),
    }

    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=payload,
        timeout=30,
    )
    if r.status_code in (200, 201):
        result = r.json()
        art_id = result[0]["id"] if isinstance(result, list) and result else "unknown"
        print(f"  ✅ Published: {article['headline'][:60]}... [{art_id[:8]}]")
        return art_id
    else:
        print(f"  ❌ Failed to publish: {r.status_code} {r.text[:300]}")
        return None


# ─── ARTICLES ───────────────────────────────────────────────────────
def build_articles():
    articles = []

    # ── ARTICLE 1: Newark Airport International Flights Threat ──
    articles.append({
        "headline": "The U.S. Just Threatened to Shut Down International Flights at Newark. The FIFA World Cup Starts in 13 Days.",
        "subheadline": "DHS Secretary Markwayne Mullin says customs officers could be pulled from sanctuary city airports, stranding millions of travelers — including the diaspora — weeks before the World Cup kicks off in New Jersey.",
        "slug": "dhs-newark-international-flights-threat-sanctuary-cities-fifa-world-cup-nri-20260529",
        "category": "news",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "USA Today", "url": "https://www.usatoday.com"},
            {"name": "U.S. Travel Association", "url": "https://www.ustravel.org"},
            {"name": "NorthJersey.com", "url": "https://www.northjersey.com"}
        ],
        "image_search": {"pexels": "Newark airport terminal international flights", "fallback": "airport departures board"},
        "image_caption": "Newark Liberty International Airport, a major gateway for international travelers and the Indian diaspora on the U.S. East Coast.",
        "body": """The Trump administration has escalated a standoff with Democratic-led cities to a point that could paralyse international air travel at some of America's busiest airports — just as the FIFA World Cup is about to begin.

On May 28, Department of Homeland Security Secretary Markwayne Mullin warned on Fox News that the U.S. government could pull Customs and Border Protection officers from Newark Liberty International Airport in New Jersey. Without those officers, no international flight can land and have its passengers processed into the country.

"If things don't change, we're going to have to make this step pretty quick," Mullin said, referring to what he described as a lack of cooperation from local law enforcement around federal immigration enforcement operations.

## What Triggered the Threat

The immediate trigger is a confrontation at Delaney Hall, an ICE-run detention facility in Newark. Detainees began a hunger strike on May 22 over conditions including alleged food shortages and lack of medical care. Protests outside the facility have grown, drawing Democratic lawmakers and immigration advocacy groups.

Senator Andy Kim of New Jersey said he was hit with pepper spray by federal officers outside Delaney Hall earlier this week. New Jersey's governor has resisted calls to deploy state police to assist federal immigration officials at the site.

Mullin framed the airport threat as a resource question: if federal officers must be diverted to protect ICE agents at detention centres, those officers cannot simultaneously process travellers at airports.

"If Customs isn't there processing international flights, then those individuals when the airlines land won't be permitted into the United States," Mullin told Fox News.

## The Sanctuary City Dimension

The threat extends well beyond Newark. Acting Attorney General Todd Blanche called halting international flight processing in sanctuary cities an "extreme" option, but one that "needed to be considered." The Department of Justice's sanctuary city list includes New York City, Los Angeles, San Francisco, Chicago, Boston, Seattle, Philadelphia, and Denver — home to some of America's largest airports.

For the Indian American community, concentrated in the New York-New Jersey metropolitan area more than almost anywhere else in the country, the implications are immediate. Newark is a United Airlines hub and a primary gateway for flights from India and the Middle East. JFK and LaGuardia, also potentially affected, handle millions of international arrivals annually.

## The World Cup Complication

The timing could not be worse. The 2026 FIFA World Cup, co-hosted by the United States, Mexico, and Canada, kicks off on June 11 — just 13 days away. MetLife Stadium in East Rutherford, New Jersey, will host the final on July 19. The tournament is expected to bring over one million international visitors to the New York-New Jersey region alone.

The U.S. Travel Association warned that removing immigration officials from Newark could cost $8 billion annually in tourist spending. The group noted that the airport processes five million Americans returning home each year, in addition to millions of foreign visitors.

"This could damage America's reputation as a welcoming destination," the association said, calling the potential action "devastating."

## What It Means for the Diaspora

Indian Americans flying in or out of Newark, JFK, or other major East Coast airports would face disruption whether or not they are U.S. citizens. Customs and Border Protection processes all international arrivals, including returning American citizens and green card holders. Without CBP officers, planes cannot deplane international passengers.

For NRIs visiting family in India, the summer travel season is already at its peak. A disruption at Newark would force travellers to reroute through airports in non-sanctuary jurisdictions — assuming those airports have capacity.

Airlines are reportedly making urgent calls to the administration and Congress. United Airlines, the dominant carrier at Newark, declined to comment publicly.

## No Action Yet, but the Threat Is Real

As of May 29, no flights have been cancelled or rerouted. The FAA, Port Authority of New York and New Jersey, and airlines have announced no changes. But the administration has made clear the option is on the table.

The standoff reflects a broader pattern: immigration enforcement disputes between the federal government and Democratic states are increasingly spilling into domains — air travel, commerce, public safety — that affect everyone, regardless of immigration status. For the 4.8 million Indian Americans in the United States, many of whom live in or travel through the cities on the sanctuary list, this is no longer a political abstraction.""",
    })

    # ── ARTICLE 2: FIFA World Cup India Broadcast Rights Crisis ──
    articles.append({
        "headline": "India Still Has No Broadcaster for the FIFA World Cup. The Tournament Starts in 13 Days.",
        "subheadline": "FIFA initially wanted $100 million for India's broadcast rights. Nobody paid. Now Zee Entertainment is in last-minute talks, an Indian American firm claims it won a secret bid, and a Delhi court is demanding free-to-air coverage. A billion fans are waiting.",
        "slug": "fifa-world-cup-2026-india-broadcast-rights-crisis-zee-jiohotstar-avni-20260529",
        "category": "news",
        "sources": [
            {"name": "Reuters", "url": "https://www.reuters.com"},
            {"name": "Exchange4Media", "url": "https://www.exchange4media.com"},
            {"name": "The Indian Eye", "url": "https://www.theindianeye.com"},
            {"name": "Business Today Malaysia", "url": "https://www.businesstoday.com.my"}
        ],
        "image_search": {"pexels": "FIFA World Cup soccer stadium crowd", "fallback": "football stadium fans cheering"},
        "image_caption": "The 2026 FIFA World Cup begins June 11, but India's 1.4 billion people still do not have a confirmed broadcaster.",
        "body": """The biggest sporting event on the planet begins in 13 days. India, a country of 1.4 billion people with a rapidly growing football audience, does not yet have a confirmed broadcaster for the 2026 FIFA World Cup.

The situation is unprecedented. FIFA has concluded broadcast agreements in more than 180 territories worldwide. China sealed a deal with state broadcaster CMG on May 15. India, the world's most populous country and a market that accounted for 2.9 percent of the 2022 World Cup's global television reach, remains a blank space on the map.

## How the Price Collapsed

FIFA initially sought approximately $100 million for the combined India broadcasting rights for the 2026 and 2030 World Cups. That figure was based on the assumption that India's growing football culture — catalysed by the Indian Super League, English Premier League fandom, and Lionel Messi's global celebrity — would attract aggressive bidding.

It did not.

JioHotstar, the Reliance-Disney joint venture that broadcast the 2022 World Cup in India, offered roughly $20 million. Sony Group explored the rights but decided not to submit an offer at all. FIFA's asking price was last reported at around $60 million — still three times what Reliance-Disney was willing to pay.

The standoff exposed an uncomfortable truth for global football's governing body: India's football market, however large in terms of eyeballs, generates a fraction of the advertising revenue that cricket commands. The Board of Control for Cricket in India's media rights for the IPL sold for $6.2 billion over five years. FIFA's entire India World Cup package could not attract a twentieth of that.

## The Last-Minute Scramble

Two developments in the past week suggest a resolution may finally be close — though neither is confirmed.

On May 26, Zee Entertainment announced it was in talks with FIFA to stream and broadcast the tournament as part of its new Unite8 Sports channel portfolio. The company disclosed no financial details.

Separately, an Indian American investment firm from Washington, D.C., named Avni LLC, claimed that an associated partner had won a bid through FIFA's closed tender process, backed by corporate guarantees exceeding $300 million. Avni LLC's CEO, Deelip Mhaske, described a vision built around OTT platforms, AI-powered multilingual broadcasting, and mobile micro-subscriptions.

The claim is extraordinary and unverified. FIFA has said only that discussions in India "are ongoing and must remain confidential at this stage."

## The Court Steps In

Meanwhile, a Delhi High Court petition is seeking to force free-to-air broadcast of the World Cup through Doordarshan and DD Sports. Advocate Avdhesh Bairwa, who filed the petition, argues that depriving millions of fans of access to the World Cup violates their fundamental rights. Justice Purushaindra Kumar Kaurav issued notice to the Centre and Prasar Bharati.

The petition points to a precedent: India's Sports Broadcasting Signals (Mandatory Sharing with Prasar Bharati) Act requires that events of national importance be made available on free-to-air television. Whether the FIFA World Cup qualifies under this provision is now a live legal question.

## Why the Diaspora Should Care

For the estimated 5 million Indian Americans in the United States, the broadcast crisis has a particular edge. Many NRIs follow the World Cup through Indian-language commentary and analysis. Without an Indian broadcaster, Hindi, Tamil, and Bengali commentary — the kind that turns a World Cup match into a cultural event, not just a sporting one — may not exist for this tournament.

Moreover, the 2026 World Cup is being co-hosted by the United States. Matches will be played in New York, Los Angeles, Houston, Dallas, San Francisco, Seattle, Boston, and Philadelphia — cities with massive Indian American populations. The possibility that friends and family back in India cannot watch the same matches that NRIs could attend in person is a strange irony.

## The Clock Is Ticking

The group stage begins on June 11 with Mexico versus South Africa at the Azteca Stadium. India's football fans will either have a broadcaster by then, or they will be reduced to searching for illegal streams of the most-watched event in world sport.

Industry sources told Exchange4Media that a formal announcement could come as early as next week, with Zee Entertainment the frontrunner. But until pen meets paper, India's World Cup remains in blackout.""",
    })

    # ── ARTICLE 3: H-1B Tech Workers Brutal Job Market + AI displacement ──
    articles.append({
        "headline": "142,000 Tech Jobs Have Been Cut in 2026. For Indian H-1B Workers, Every Layoff Is a Deportation Clock.",
        "subheadline": "AI is replacing junior developers at scale, companies are hiring in Bangalore instead of Boston, and H-1B holders who lose their jobs have 60 days before they must leave the country. The American tech dream is fracturing along visa lines.",
        "slug": "tech-layoffs-2026-h1b-indian-workers-ai-displacement-deportation-risk-20260529",
        "category": "news",
        "sources": [
            {"name": "TechTimes", "url": "https://www.techtimes.com"},
            {"name": "American Bazaar", "url": "https://www.americanbazaaronline.com"},
            {"name": "Stanford HAI 2026 AI Index", "url": "https://hai.stanford.edu"},
            {"name": "TNGlobal", "url": "https://technode.global"}
        ],
        "image_search": {"pexels": "software developer office worried stressed", "fallback": "tech worker computer office"},
        "image_caption": "Indian tech professionals on H-1B visas face a unique double bind: lose your job, and the clock starts ticking on your legal right to stay in the country.",
        "body": """The numbers are stark. According to tracking data compiled by multiple industry analysts, 142,000 technology workers worldwide have been laid off in 2026. If the pace holds, the year will surpass 2025's brutal toll of 245,000 job cuts. For Indian-origin professionals in the United States — who hold the majority of H-1B work visas — every one of these layoffs carries a consequence that no American citizen faces: a 60-day window to find a new employer or leave the country.

## The AI Displacement Is Real and Targeted

A Stanford University study published in April — the HAI 2026 AI Index — found that employment for software developers aged 22 to 25 fell nearly 20 percent since 2024. Developers aged 30 and older at the same companies saw headcount grow during the same period.

The mechanism is precise: generative AI tools are not eliminating software engineering as a discipline. They are eliminating the specific tasks that junior developers were hired to perform — boilerplate code, basic operations, scripted testing, and routine bug fixes. The result is that companies need fewer entry-level engineers, which is exactly the rung where many H-1B workers begin their American careers.

Boston Consulting Group projects that up to 15 percent of U.S. jobs could be eliminated over the next five years. One-third of surveyed organisations told Stanford researchers they expect AI to reduce their workforce within the next year, with the deepest cuts in service operations, supply chain management, and software engineering.

## The H-1B Trap

The structural cruelty of the H-1B system is that it ties a worker's legal presence in the United States to continuous employment. When an H-1B holder is laid off, they have 60 days — recently extended from zero under a Biden-era rule that the Trump administration has not reversed — to find a new sponsor or begin departure proceedings.

An anonymous post on a popular professional forum, widely reported by the American Bazaar this week, captured the desperation: one Indian data engineering leader described applying to more than 2,000 positions after being laid off, reaching dozens of recruiter rounds before finally securing an offer at a FAANG company.

"The job market is tough for U.S. citizens as it is," one commenter wrote. "H-1Bs have it worse considering companies want nothing to do with the immigration headache."

Others described living in constant fear, unable to leave jobs they disliked because changing employers has become too risky. Rent, healthcare costs, childcare expenses, and immigration legal fees have become overwhelming for families with a single income tied to visa sponsorship.

## Companies Are Hiring in India Instead

The displacement is not just about AI. Major U.S. technology companies are accelerating the shift of roles to India, where engineering talent costs a fraction of American salaries. A survey by the anonymous professional network Blind found that 38 percent of respondents anticipated that hiring surges in Bangalore, Hyderabad, and Pune would directly replace existing U.S. roles.

This creates a perverse dynamic for the Indian diaspora. The same talent pipeline that once made Indian engineers the backbone of Silicon Valley is now being used to undercut their positions — not by immigrants undercutting American workers, as the political narrative often frames it, but by American companies choosing to hire the same talent pool at home in India, where there are no visa complications and salaries are lower.

Meta laid off nearly 1,400 employees in Washington state alone this week, part of an ongoing restructuring. Cloudflare cut 1,100 jobs in May. TCS announced plans to eliminate 12,000 positions globally. The pattern is consistent: companies that over-hired between 2020 and 2023 are restructuring with AI as both the rationale and the mechanism.

## The Skills Divide

The tech layoff wave is not uniform. Roles in machine learning infrastructure, model evaluation, AI safety, and applied research remain in acute shortage. Traditional software engineering, product management, recruiting, and back-office positions face contraction.

The skills these growing roles require cannot be quickly acquired by the workers most exposed to the current wave. A mid-career Java developer or QA engineer cannot retrain as an AI safety researcher in 60 days — the same 60 days that an H-1B holder has to find new sponsorship.

## Some Are Choosing to Leave

Perhaps the most telling signal is that some Indian tech workers are no longer waiting to be forced out. "I am leaving this country this September and going back home to build there, finally," one commenter wrote on a professional forum. "I want to contribute to India's growth story."

For a generation of Indian engineers who moved to the United States chasing the promise of meritocratic opportunity, this represents a quiet but significant reversal. The American dream they pursued has not disappeared, but its terms have changed. The question many are now asking is whether those terms still favour the people who built so much of America's technology industry.

For the 4.8 million Indian Americans, and particularly for the hundreds of thousands on temporary work visas, the answer is no longer obvious.""",
    })

    return articles


# ─── MAIN ───────────────────────────────────────────────────────────
if __name__ == "__main__":
    articles = build_articles()
    published = []

    for i, article in enumerate(articles, 1):
        print(f"\n{'='*60}")
        print(f"Article {i}/{len(articles)}: {article['headline'][:60]}...")
        print(f"{'='*60}")

        # Image sourcing
        img_url = None
        search = article.get("image_search", {})

        # Try Pexels (no person article here)
        if search.get("pexels"):
            img_url = fetch_pexels_image(search["pexels"], search.get("fallback"))

        # Validate and upload
        if img_url:
            if validate_image(img_url):
                filename = f"{article['slug']}.jpg"
                final_url = upload_image_to_supabase(img_url, filename)
                article["image_url"] = final_url
            else:
                print("  ⚠ Image validation failed, publishing without image")
                article["image_url"] = None
        else:
            print("  ⚠ No image found, publishing without image")
            article["image_url"] = None

        # Publish
        art_id = publish_article(article)
        if art_id:
            published.append({"id": art_id, "slug": article["slug"], "headline": article["headline"]})
        
        time.sleep(1)  # rate limiting

    print(f"\n{'='*60}")
    print(f"DONE: Published {len(published)}/{len(articles)} articles")
    for p in published:
        print(f"  • {p['headline'][:60]}... [{p['id'][:8]}]")
    print(f"{'='*60}")
