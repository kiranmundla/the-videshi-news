#!/usr/bin/env python3
"""Insert V3 articles into Supabase using curl."""
import json, os, subprocess, sys, tempfile

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
STORAGE_BASE = f"{SUPABASE_URL}/storage/v1/object/public/article-images"

def supabase_post(path, data):
    url = f"{SUPABASE_URL}{path}"
    payload = json.dumps(data)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write(payload)
        tmppath = f.name
    try:
        r = subprocess.run([
            "curl", "-s", "-X", "POST", url,
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", f"@{tmppath}"
        ], capture_output=True, timeout=30)
        stdout = r.stdout.decode("utf-8")
        return json.loads(stdout)
    except Exception as e:
        print(f"POST error: {e}", file=sys.stderr)
        return None
    finally:
        os.unlink(tmppath)

def supabase_patch(path, data):
    url = f"{SUPABASE_URL}{path}"
    payload = json.dumps(data)
    r = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "PATCH", url,
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-d", payload
    ], capture_output=True, timeout=30)
    return r.stdout.decode("utf-8").strip()

articles = []

# ── Article 1: Mbappe/Deschamps ──
articles.append({
    "headline": "Mbappe Says France 'Failed' Deschamps as Captain Issues Emotional Farewell Before England Clash",
    "subheadline": "The Real Madrid forward posted a heartfelt Instagram tribute to the outgoing manager ahead of Saturday's World Cup third-place playoff, calling Deschamps one of France's 'greatest legends.'",
    "slug": "mbappe-says-france-failed-deschamps-emotional-farewell",
    "category": "sports",
    "vertical": "sports",
    "article_type": "breaking",
    "status": "published",
    "topic_id": "00f6bcf2-fd4d-4dd0-b950-ccb16b48efb4",
    "tags": ["World Cup 2026", "France", "Kylian Mbappe", "Didier Deschamps", "England", "Zidane", "football"],
    "sources": [
        "https://www.thesun.ie/sport/football/15478123/mbappe-deschamps-france-failed-world-cup/",
        "https://www.reuters.com/sports/soccer/deschamps-last-dance-mbappe-record-chase-give-unwanted-third-place-game-edge-2026-07-17/",
        "https://supersport.com/football/world-cup/news/deschamps-set-for-bittersweet-ending-to-france-reign-as-zidane-waits",
        "https://www.reuters.com/sports/soccer/frances-golden-generation-left-heartbroken-zidane-era-beckons-2026-07-15/"
    ],
    "diaspora_angle": "Major World Cup storyline relevant to millions of Indian football fans following the tournament closely.",
    "word_count": 680,
    "image_url": f"{STORAGE_BASE}/mbappe-says-france-failed-deschamps-emotional-farewell.jpg",
    "image_caption": "Kylian Mbappe during France's opening World Cup match against Senegal in June 2026. The captain posted an emotional Instagram tribute to outgoing manager Didier Deschamps ahead of Saturday's third-place playoff.",
    "image_attribution": "Wikimedia Commons",
    "body": '<div class="key-takeaways"><ul><li>Kylian Mbappe posted an emotional Instagram tribute to Didier Deschamps, saying France "failed" to give him a fitting send-off after their World Cup semifinal loss to Spain.</li><li>Deschamps ends his 14-year reign as France manager on Saturday in the third-place playoff against England in Miami.</li><li>Mbappe has scored eight goals this tournament and is tied with Lionel Messi for the Golden Boot heading into the match.</li><li>Zinedine Zidane is widely expected to succeed Deschamps as the next France head coach.</li></ul></div><p>Kylian Mbappe posted a heartfelt tribute to outgoing France manager Didier Deschamps on Saturday morning, hours before the World Cup third-place playoff against England in Miami. In an Instagram message that carried the weight of a decade-long partnership, the France captain said his team had let down the man who transformed French football.</p><p>"Today is your last dance," Mbappe, 27, wrote. "You who gave us so much. We should have offered you a better ending, but we failed."</p><blockquote class="pull-quote"><p>"Putting words to what you brought over 14 years is very difficult, so major an actor were you in the revival of this team. People haven\'t always known how to appreciate your greatness, but time and history will take care of that."</p><cite>\u2014 Kylian Mbappe, France captain</cite></blockquote><h2>A 14-Year Reign That Reshaped French Football</h2><p>Deschamps took charge of Les Bleus in 2012, inheriting a squad still reeling from the chaos of the 2010 World Cup, when a player revolt and training boycott plunged French football into crisis. He rebuilt the national team from the ground up, leading France to the 2018 World Cup title in Russia \u2014 20 years after captaining the side to their first global crown in 1998.</p><p>Under Deschamps, France reached three consecutive World Cup semifinals and two finals, losing to Argentina on penalties in 2022 before falling 2-0 to Spain in this tournament\'s last four. His pragmatic emphasis on balance, discipline, and tournament management repeatedly delivered results, even if critics argued he did not always maximize the attacking riches at his disposal.</p><p>Mbappe has earned all 105 of his international caps under Deschamps, who handed the then-18-year-old his senior debut in 2017. In his message, the Real Madrid forward called the manager "one of the greatest legends of our country."</p><h2>Golden Boot Race and One Last Match</h2><p>Saturday\'s match at Hard Rock Stadium offers France one last chance to end the tournament on a positive note \u2014 and gives Mbappe a shot at individual history. The 27-year-old has scored eight goals this World Cup and 20 in his career at the tournament, leaving him tied with Argentina\'s Lionel Messi at the top of the Golden Boot standings.</p><p>Deschamps confirmed Mbappe would be available for selection but indicated he planned to rotate his lineup significantly. "I had the privilege of experiencing moments that were magical, and others that were difficult," Deschamps said on the eve of the match. "But life goes on. I\'m a positive person, and I know things will be good, too. It\'s the best thing that ever happened to me."</p><p>England manager Thomas Tuchel acknowledged the emotional stakes. "None of our players or none of the French players want to play in this match," Tuchel said. "Everyone plays to win the World Cup, but it is what it is."</p><h2>Zidane Waits in the Wings</h2><p>Zinedine Zidane has not been officially appointed as Deschamps\' successor, but the former France captain and Real Madrid coach is widely regarded as the natural heir. According to Reuters, Zidane would inherit a squad far stronger than the one Deschamps took over in 2012, with France able to draw on a generation of talent unmatched by most rivals.</p><p>The challenge for Zidane, should he take charge, would be less about finding players than finding the structure to bring the best out of them collectively. France\'s semifinal collapse against Spain highlighted a recurring issue: a squad loaded with individual brilliance but struggling to function as a cohesive unit under pressure.</p><h2>What\'s Next</h2><p>The France-England third-place playoff kicks off Saturday evening at Hard Rock Stadium in Miami. The World Cup final between Spain and Argentina follows on Sunday at MetLife Stadium in East Rutherford, New Jersey. Regardless of the result, Deschamps\' final match will mark the end of an era that produced France\'s second World Cup title and established Les Bleus as one of the most consistent forces in international football.</p>'
})

# ── Article 2: US bill on Russian oil / India ──
articles.append({
    "headline": "India Flags 'Double Standards' as US Senate Bill Threatens 100% Tariffs on Russian Oil Buyers",
    "subheadline": "New Delhi warns the bipartisan legislation \u2014 which exempts European gas importers while targeting India, China, and three other nations \u2014 could damage bilateral ties and ongoing trade negotiations.",
    "slug": "india-flags-double-standards-us-senate-bill-100-tariff-russian-oil",
    "category": "markets-finance",
    "vertical": "markets-finance",
    "article_type": "breaking",
    "status": "published",
    "topic_id": "8566a3ff-b83f-4e70-bdb7-e0cb0839a2a6",
    "tags": ["India", "US", "Russia", "oil", "tariffs", "sanctions", "trade", "Lindsey Graham"],
    "sources": [
        "https://www.outlookbusiness.com/news/india-flags-double-standards-as-us-softens-russia-sanctions-bill",
        "https://www.reuters.com/world/us-russia-sanctions-bill-eases-threat-tariffs-china-india-2026-07-14/",
        "https://www.thehindubusinessline.com/news/world/us-senate-bill-seeks-100-tariffs-on-india-china-for-buying-russian-oil/article69820123.ece",
        "https://www.outlookbusiness.com/news/us-senate-bill-seeks-100-tariffs-on-india-4-other-nations-for-buying-russian-oil"
    ],
    "diaspora_angle": "The proposed tariffs could affect all Indian exports to the US, directly impacting trade flows, Indian IT services, and NRI business interests in both countries.",
    "word_count": 720,
    "image_url": f"{STORAGE_BASE}/india-flags-double-standards-us-senate-bill-100-tariff-russian-oil.jpg",
    "image_caption": "An oil refinery complex with industrial towers and piping. India\'s purchases of discounted Russian crude have surged since 2022, reaching record levels in June 2026.",
    "image_attribution": "Pexels",
    "body": '<div class="key-takeaways"><ul><li>A bipartisan US Senate bill named after the late Senator Lindsey Graham would impose up to 100% tariffs on the top five buyers of Russian oil, including India and China.</li><li>India has called the legislation "double standards," noting it exempts European nations importing Russian natural gas while penalizing countries buying crude oil.</li><li>The bill has over 60 Senate co-sponsors and President Trump\'s backing, though it includes a presidential waiver provision.</li><li>India imported $55.37 billion in goods from Russia in FY26, with crude imports hitting record highs in June amid Gulf energy disruptions.</li></ul></div><p>India has pushed back against a proposed US Senate bill that would impose tariffs of up to 100% on the world\'s largest buyers of Russian oil, warning that the measure adopts "double standards" by exempting European nations that import Russian natural gas. The response, reported by The Economic Times and Outlook Business, comes as the legislation gains momentum with bipartisan support and a green light from President Donald Trump.</p><p>The bill \u2014 formally named the Lindsey O. Graham Sanctioning Russia Act of 2026, in tribute to the late Republican senator who championed it \u2014 was introduced on Thursday with more than 60 Senate co-sponsors. It targets China, India, Slovakia, Hungary, and Azerbaijan as the top five purchasers of Russian crude, while shielding countries whose Russian gas imports account for less than 15% of Moscow\'s total natural gas exports.</p><blockquote class="pull-quote"><p>"The US is not taking the right approach. These are double standards vis-a-vis Europe and may not achieve the desired result. The move has the potential to damage relations with India even further."</p><cite>\u2014 Indian government source, via The Economic Times</cite></blockquote><h2>What the Bill Proposes</h2><p>The legislation authorizes tariffs of up to 100% on imports from the top five purchasers of Russian crude oil or nations identified as top facilitators of Russian oil sanctions evasion. It also targets Russia\'s shadow fleet of oil tankers, the Central Bank of the Russian Federation, and major state-owned energy projects including Yamal LNG and Arctic LNG.</p><p>The current bill is a scaled-down version of the original proposal introduced in April 2025, which envisaged blanket tariffs of 500%. According to Reuters, the softer approach reflects months of negotiations to secure Trump\'s support without alienating strategic partners.</p><p>A key provision gives Trump the authority to waive sanctions entirely if he determines it is in the US national interest \u2014 a clause that could prove critical given the ongoing India-US trade deal negotiations. The US Trade Representative would also reassess the list of top purchasers every 180 days, adjusting tariffs based on changes in buying patterns.</p><h2>India\'s Energy Calculus</h2><p>India\'s concerns go beyond the tariff rate. Since Russia\'s invasion of Ukraine in 2022, India has substantially increased imports of discounted Russian crude as Western buyers pulled back. India imported goods worth $55.37 billion from Russia during FY26, according to Ministry of Commerce data. Although annual imports declined 13.23% year-on-year, they rebounded sharply in recent months \u2014 rising 18.06% to $7.35 billion in April 2026 alone.</p><p>India\'s crude imports from Russia reached a record high in June following disruptions to Gulf energy supplies amid the Iran-Israel conflict. Russian crude now accounts for roughly 35% of India\'s total crude oil imports, and India has become one of the top refiners of Russian crude for jet fuel and diesel, according to The Hindu BusinessLine.</p><p>Government sources argue that India\'s purchases are driven by energy security considerations and market conditions rather than geopolitical alignment. They also contend that targeting India would not achieve Washington\'s stated objective. "China will find a way to continue importing Russian oil notwithstanding any sanctions," one source told The Economic Times.</p><h2>Collision Course With Trade Talks</h2><p>The legislation lands at a particularly awkward moment. India and the United States are in the final stages of negotiating a bilateral trade agreement, and the two countries have deepened cooperation across defense, technology, and the Quad framework. Washington is simultaneously pursuing a separate 10% tariff on Indian goods and has proposed Section 301 duties \u2014 measures that Indian officials warned could strain ties in a separate development this week.</p><p>Senator Richard Blumenthal, the bill\'s co-author, has urged Congress to move forward without adding new provisions targeting Iran and Hezbollah, which Trump has suggested. "With all due respect to the President, he has approved this bill, and we should move forward with this bill rather than opening it to other potential targets," Blumenthal told reporters.</p><h2>What\'s Next</h2><p>The bill still needs to clear the full Senate and the House before becoming law. Its presidential waiver provision means that even if passed, the tariffs may never be imposed \u2014 particularly if India and the US reach a trade deal that satisfies both sides. But the legislative signal alone could reshape energy markets and accelerate India\'s efforts to diversify its crude sources away from Russian dependence.</p>'
})

# ── Article 3: OnePlus exits US/Europe ──
articles.append({
    "headline": "OnePlus Exits the US and Europe, Doubles Down on India as Oppo Restructures Global Operations",
    "subheadline": "The Chinese smartphone maker confirmed it will stop launching new products in North America and Europe, while insisting India remains a priority market \u2014 but a Bloomberg report suggests India could follow by 2027.",
    "slug": "oneplus-exits-us-europe-doubles-down-india-oppo-restructures",
    "category": "technology",
    "vertical": "technology",
    "article_type": "breaking",
    "status": "published",
    "topic_id": "8ef92069-f28d-491a-b5f0-c416243b180d",
    "tags": ["OnePlus", "Oppo", "smartphones", "India", "technology", "OxygenOS", "ColorOS"],
    "sources": [
        "https://www.gadgets360.com/mobiles/features/oneplus-exits-us-and-europe-continues-operations-in-india-5-things-to-know-11782794",
        "https://www.gsmarena.com/oneplus_officially_exits_europe_and_north_america_will_continue_in_india-news-69123.php",
        "https://www.thehindubusinessline.com/info-tech/oneplus-once-popular-with-tech-fans-to-pull-out-of-us-and-europe/article69818234.ece",
        "https://wccftech.com/oneplus-exit-markets-analyst-identity/"
    ],
    "diaspora_angle": "OnePlus has a massive fan base among Indian tech consumers and NRIs. Indians in the US and Europe who rely on OnePlus devices will lose access to new models, while India-based users face uncertainty about the brand\'s long-term future.",
    "word_count": 700,
    "image_url": f"{STORAGE_BASE}/oneplus-exits-us-europe-doubles-down-india-oppo-restructures.jpg",
    "image_caption": "Modern smartphones arranged on a flat surface. OnePlus confirmed it will stop launching new products in the US and Europe while continuing operations in India.",
    "image_attribution": "Pexels",
    "body": '<div class="key-takeaways"><ul><li>OnePlus confirmed it will cease all new product launches in the US and Europe, with the OnePlus 15 as the last device for those markets.</li><li>India operations will continue "as usual," with the OnePlus N6x confirmed as the next upcoming launch.</li><li>All eligible OnePlus devices globally will transition from OxygenOS to Oppo\'s ColorOS with Android 17.</li><li>A Bloomberg report suggests OnePlus may exit India by 2027 as part of a broader Oppo restructuring, though the company has not confirmed this.</li></ul></div><p>OnePlus has confirmed one of the most dramatic retreats in recent smartphone history. The brand that built a cult following with aggressively priced Android flagships will stop launching new products in the United States and Europe, the company announced this week. The move is part of a broader restructuring by parent company Oppo, which is consolidating its global smartphone operations amid slowing sales, rising costs, and escalating geopolitical pressures.</p><p>The OnePlus 15 will be the last device the brand sells in North America and Europe. Existing customers will continue to receive software updates, security patches, and warranty support, but no new hardware is coming.</p><h2>India Stays \u2014 For Now</h2><p>In a separate statement, OnePlus said India remains "one of its most important markets" and that local operations are "on track." The company pointed to the recently launched OnePlus N6 and confirmed the upcoming N6x as part of its India roadmap \u2014 a budget-focused device teased on Amazon India with an 8,000mAh battery that could become the brand\'s most affordable phone yet.</p><p>"India continues to be one of OnePlus\' most important markets, and our commitment to our users, partners, and community remains unwavering," the company said in a statement.</p><p>But a Bloomberg report cast a longer shadow. Citing a person familiar with the matter, Bloomberg reported that Oppo plans to wind down OnePlus operations globally, with India potentially following the US and Europe by sometime in 2027. If that happens, China would be the only major market where OnePlus continues to operate. Neither OnePlus nor Oppo has confirmed the 2027 timeline.</p><h2>OxygenOS Is Dead, Long Live ColorOS</h2><p>Alongside the market exit, OnePlus announced that all eligible devices will transition from OxygenOS \u2014 the brand\'s distinctive Android skin \u2014 to Oppo\'s ColorOS following the release of Android 17 later this year. The change will be voluntary for users with supported devices, but the direction is clear: OnePlus is being folded more deeply into Oppo\'s software ecosystem.</p><p>The company framed the move as a way to "streamline software development, accelerate update delivery, and make better use of shared engineering and R&D capabilities." For longtime fans, the loss of OxygenOS marks the end of a key differentiator that originally set OnePlus apart from its Oppo parent.</p><h2>Why OnePlus Is Retreating</h2><p>OnePlus has not disclosed a single reason for the pullback, describing it only as a "proactive global strategy adjustment." But reports and analysts point to several converging pressures.</p><p>Global smartphone shipments fell 11% year-on-year in Q2 2026 \u2014 the weakest April-to-June quarter since 2013, according to Counterpoint Research. Rising DRAM and memory prices have squeezed margins across the industry, particularly for brands competing on price rather than ecosystem lock-in.</p><p>Geopolitical friction has added to the strain. Apple sued Oppo and a former Apple employee in US federal court in August 2025, alleging trade secret theft related to Apple Watch health-sensing technology. Oppo denied wrongdoing, but the case remains active. OnePlus India CEO Robin Liu resigned in March 2026, and co-founder Carl Pei left back in 2020 to start rival brand Nothing \u2014 which, in an ironic twist, just became India\'s fastest-growing smartphone brand in Q2 2026, according to Counterpoint.</p><blockquote class="pull-quote"><p>"OnePlus did not necessarily fail on product. It struggled to maintain a distinctive identity."</p><cite>\u2014 Industry analyst, via WCCFTech</cite></blockquote><h2>What Happens to Your OnePlus Phone</h2><p>For current OnePlus owners in the US and Europe, the company has pledged continued software updates and security patches through each device\'s support lifecycle. Customer service channels will remain open, and warranty obligations will be honored. The North American Community website and app will shut down on August 16, 2026. European community forums and stores will remain open for now, but retail stock will be sold off without restocking.</p><h2>What\'s Next</h2><p>The immediate question for Indian consumers is whether the Bloomberg report\'s 2027 exit timeline proves accurate. OnePlus still commands a devoted user base in India, particularly in the premium mid-range segment. If the brand does withdraw, the market would likely see Nothing, Samsung, and Xiaomi absorb its share \u2014 a scenario that would have been unthinkable when OnePlus first disrupted the market with its "Never Settle" philosophy in 2013.</p>'
})

# ── Insert all articles ──
inserted_ids = []
for i, art in enumerate(articles):
    result = supabase_post("/rest/v1/p2_articles", art)
    if result and isinstance(result, list):
        aid = result[0]["id"]
        inserted_ids.append((aid, art["topic_id"], art["headline"], art["category"]))
        print(f"\u2705 Article {i+1}: {art['headline'][:70]}... \u2192 {aid}")
    else:
        inserted_ids.append((None, art["topic_id"], art["headline"], art["category"]))
        print(f"\u274c Article {i+1} FAILED: {art['headline'][:70]}...")

# ── Update topic statuses ──
print("\n--- Updating topic statuses ---")
for aid, tid, headline, cat in inserted_ids:
    if aid:
        status = supabase_patch(
            f"/rest/v1/p2_topics?id=eq.{tid}",
            {"status": "published", "last_article_id": aid}
        )
        print(f"  Topic {tid[:8]}... \u2192 {status}")

# Also mark skipped Spain topic as rejected
spain_tid = "893d402c-bc42-4c95-b412-c939e7a67c2a"
status = supabase_patch(
    f"/rest/v1/p2_topics?id=eq.{spain_tid}",
    {"status": "rejected"}
)
print(f"  Spain topic (skipped/dedup) \u2192 {status}")

print("\n--- Summary ---")
for aid, tid, headline, cat in inserted_ids:
    s = "\u2705" if aid else "\u274c"
    print(f"  {s} [{cat}] {headline}")
print(f"\n  Skipped: [sports] Spain's Road To FIFA World Cup 2026 Final (dedup with existing 'Spain vs Argentina' article)")
