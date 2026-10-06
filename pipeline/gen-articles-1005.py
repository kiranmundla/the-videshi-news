#!/usr/bin/env python3
"""Stage 3 writer articles as JSON in pipeline/.state/."""
import json, re, html as ihtml

STATE = "/home/hatch/workspace/the-videshi-news/pipeline/.state"

def wc(body):
    text = re.sub(r"<[^>]+>", " ", body)
    text = ihtml.unescape(text)
    return len(text.split())

# ---------------------------------------------------------------- ARTICLE 1
body1 = """<div class="key-takeaways"><ul><li>The film's India net collection fell sharply on Day 4 (Monday), with trade trackers projecting around Rs 20 crore for the day against Rs 61 crore on Sunday.</li><li>Despite the dip, <em>Drishyam 3: The Conclusion</em> crossed Rs 300 crore in worldwide gross within four days of release, according to Business Today and The Times of India.</li><li>It is the second film of 2026 after <em>Dhurandhar 2</em> to come this close to the Rs 300-crore mark in just four days.</li><li>Three-day totals: Rs 176.5 crore net in India, Rs 211.8 crore India gross, Rs 61 crore overseas, and Rs 272.8 crore worldwide gross.</li></ul></div>
<h2>The Monday dip</h2>
<p>The first Monday is always the truth serum of a Bollywood opening, and <em>Drishyam 3: The Conclusion</em> was no exception. After a blockbuster Gandhi Jayanti weekend, the Ajay Devgn thriller saw its collections fall sharply on Day 4, with trade tracker projections putting Monday's India net at around Rs 20 crore — down from Rs 61 crore on Sunday. Live tracking from Sacnilk showed the film had added Rs 2.28 crore by the middle of the day across 5,377 shows, with morning occupancy in the 13-15 per cent range and afternoon shows in the 20-25 per cent band.</p>
<p>The drop was expected: the film released on Friday, October 2, riding a national holiday, and the weekend numbers were always going to be front-loaded. The Times of India's box-office report put it plainly — a big dip in collections on the first Monday. The question now is whether the film holds through the weekdays or slides the way big-holiday openers often do.</p>
<h2>A blockbuster opening weekend</h2>
<p>Whatever Monday brought, the weekend belonged to Vijay Salgaonkar. The film opened to Rs 62 crore net on Day 1 across 15,759 shows — a gross of Rs 74.4 crore — and added Rs 53.5 crore net on Day 2 across 16,868 shows, taking the two-day India net to Rs 115.5 crore. Day 3 rebounded to Rs 61 crore net across 17,323 shows, nearly matching opening-day numbers and pushing the three-day India net to Rs 176.5 crore, with the India gross at Rs 211.8 crore.</p>
<p>Overseas markets kept pace: the film added Rs 20 crore internationally on both Day 2 and Day 3, taking the three-day overseas gross to Rs 61 crore. Combined with the domestic numbers, the worldwide gross stood at Rs 272.8 crore after three days. Day 1 alone made it the second-biggest Bollywood debut of 2026 worldwide, and its 24.58 lakh day-one footfalls were Bollywood's 10th-highest post-COVID.</p>
<h2>Story over spectacle</h2>
<p>What makes the run remarkable is what the film is: a dialogue-driven thriller, not an action spectacle. As Her Zindagi noted, <em>Drishyam 3</em> is now the second film of 2026 after <em>Dhurandhar 2</em> to come this close to Rs 300 crore in just four days — and for a thriller that depends on its story more than big action set-pieces, that is a genuine outlier. The franchise's conclusion, directed by Abhishek Pathak and jointly produced by Panorama Studios and Star Studios, brings back Ajay Devgn as Vijay Salgaonkar, with Tabu as Meera Deshmukh, Jaideep Ahlawat as SP Rajveer Singh Tomar, Prakash Raj as Adv. Indrajith Shetty, and Shriya Saran, Ishita Dutta, Rajat Kapoor, Saurabh Shukla and Kamlesh Sawant in the ensemble.</p>
<h2>What to watch</h2>
<p>The Rs 200-crore India net milestone is within striking distance, and the weekday trend will decide whether the film is merely a hit or a full-blown blockbuster. With no major Hindi release crowding its second weekend, the film has a clear runway — but the Monday dip shows it must now earn its audience on the strength of word of mouth rather than the holiday surge.</p>"""

# ---------------------------------------------------------------- ARTICLE 2
body2 = """<div class="key-takeaways"><ul><li>The Government e-Marketplace handled purchases worth Rs 5.03 lakh crore in FY26; startups received just over Rs 19,000 crore — under 4 per cent of the total.</li><li>Micro and small enterprises crossed 47 per cent of GeM value because a 25 per cent procurement mandate exists; startups got entry-side exemptions but no buyer-side target.</li><li>Defence and space broke through only after changing how the state buys — iDEX's no-re-tender route, the 2025 Defence Procurement Manual, and the SSLV transfer to HAL.</li><li>The proposal: a "1% Purchase Order Mission" — earmarking 1 per cent of central procurement for startups would create roughly Rs 5,000 crore a year in demand, with no new subsidies.</li></ul></div>
<h2>The number that explains everything</h2>
<p>The Government e-Marketplace — the platform through which the Indian state buys everything from laptops to locomotives — handled purchases worth Rs 5.03 lakh crore in FY26. Startups received just over Rs 19,000 crore of that, less than four per cent. Fewer than one in five DPIIT-recognised startups is even registered as a government seller. The Standing Committee on Commerce found that only ten per cent of recognised startups had ever transacted on GeM at all, worth Rs 14,000 crore across eight financial years.</p>
<p>The contrast with micro and small enterprises is the point. MSEs account for 47.1 per cent of GeM's gross merchandise value — Rs 2.36 lakh crore — because a mandate exists: every central ministry, department and public sector enterprise must source at least 25 per cent of annual procurement from MSEs. Across CPSEs and departments in 2024-25, MSE procurement reached Rs 93,017 crore, or 43.58 per cent — comfortably above the floor. MSEs have a procurement mandate; startups have exemptions. One tells the buyer you must buy. The other tells the startup you may apply.</p>
<h2>A capital stack with no demand stack</h2>
<p>Nobody can accuse India of under-funding its founders. Over the last decade the country assembled one of the most elaborate public capital stacks for startups anywhere outside the US and China. The Fund of Funds for Startups has mobilised over Rs 25,500 crore into more than 1,370 startups through 145 alternative investment funds, topped up with another Rs 10,000 crore in 2026 through the Startup India Fund of Funds 2.0. The Seed Fund Scheme added Rs 945 crore across roughly 300 incubators. The Rs 1 lakh crore Research, Development and Innovation Fund began flowing in May, with the Technology Development Board signing its first agreements with five deep-tech companies.</p>
<p>What India did not build is a public demand stack. On the buying side there is no target, no dedicated procurement route, no reporting line. Rules 170 and 173 of the General Financial Rules exempt recognised startups from earnest money deposits and allow relaxation of prior turnover and experience — which gets a startup into the tender, but does nothing about qualification criteria written around a reference installation the company cannot possibly have.</p>
<blockquote class="pull-quote"><p>"A grant is administratively safe. A purchase order requires institutional courage."</p><cite>— YourStory</cite></blockquote>
<h2>The room where the problem became visible</h2>
<p>On August 19, in an auditorium at IIT Madras, Petroleum Secretary Neeraj Mittal promised a room full of deep-tech founders that around thirty energy startups would each become eligible for up to Rs 2 crore in milestone-linked convertible funding under a new accelerator, MC2+ Ignite, plus pilot sites inside the research centres of the oil and gas PSUs. The chairmen of ONGC, Oil India, Indian Oil, BPCL, HPCL and Engineers India were in the room — between them commanding one of the largest procurement budgets in the economy. And yet the way to promise thirty founders a customer was to build an accelerator: approving a grant is institutionally safer than awarding a purchase order to a three-year-old company.</p>
<h2>Defence and space wrote the playbook</h2>
<p>Two sectors broke through in the last five years, and both are the ones where the state changed how it buys rather than only how it funds. Innovations for Defence Excellence, launched in 2018, put grants behind startups solving service problem statements — but the decisive move was procurement: the Defence Acquisition Procedure 2020 created a category through which the services can buy iDEX-developed products without competitive re-tendering. The 2025 Defence Procurement Manual then rewrote the contract itself: liquidated damages waived during development, cut to 0.1 per cent per week for indigenisation, and assured orders for five years, extendable by five more. Space followed the same logic: IN-SPACe became a single-window regulator, the SSLV technology went to Hindustan Aeronautics Limited in a Rs 511 crore, ten-year arrangement, and in July 2026 Skyroot's Vikram-1 reached orbit — India's first privately developed orbital rocket launch. Asked what the sector still needs, IN-SPACe chairman Pawan Goenka answered in a line: the government has to be an anchor customer.</p>
<h2>What comes next</h2>
<p>The fixes need no new money — and several states are already ahead of the Centre. Kerala allows direct purchase from registered startups up to Rs 50 lakh with a Rs 3 crore ceiling; Telangana offers a 15 per cent price preference, a bilateral route with no tender floated, and 30-day deemed-approval clocks; Maharashtra requires departments to earmark 0.5 per cent of budgets for innovation; Karnataka's 2025-30 policy positions the state as first customer for deep-tech. The national proposal is a "1% Purchase Order Mission" : earmark one per cent of central procurement for DPIIT-recognised startups with a public reporting line; let a successful government-funded pilot convert into an order; create startup-specific contract terms; and publish ministry-wise procurement every quarter. On FY26 GeM volumes, one per cent would mean roughly Rs 5,000 crore in annual demand. It is payment for products and services the government already needs. A country does not create great technology companies only by financing experimentation. It creates them by becoming the first believer, the first reference and — when the product works — the first customer.</p>"""

# ---------------------------------------------------------------- ARTICLE 3
body3 = """<div class="key-takeaways"><ul><li>ThePrint's Economix analysis found paneer costs nearly twice as much as chicken and fish — and nearly seven times more per gram of protein than masoor dal — making it the costliest protein for vegetarian households.</li><li>More than 70 per cent of Indians fail to meet their daily protein requirements; Indian diets run 60 to 70 per cent carbohydrates.</li><li>The government launched an Rs 11,440-crore Mission for Atmanirbharta in pulses (FY26–FY31), targeting 35 million tonnes of production by FY31, after imports hit a record $5.5 billion in FY25.</li><li>Reuters reported the government is weighing cuts to pulse import duties after a weak monsoon raised concerns over domestic crop production and food inflation.</li></ul></div>
<h2>The protein hierarchy</h2>
<p>For vegetarian households, paneer sits at the top of the protein hierarchy — and at the top of the price list too. In its Economix analysis, ThePrint's consulting editor for economics Bidisha Bhattacharya broke down the economics of protein inflation: paneer costs nearly twice as much as chicken and fish, and for families that abstain from eggs or meat, dairy is the primary protein source beyond dal. The starkest number: paneer costs nearly seven times more per gram of protein than masoor dal.</p>
<p>That matters because protein is the nutrient India is shortest of. National nutrition surveys indicate more than 70 per cent of Indians fail to meet daily protein requirements, and the Indian diet runs 60 to 70 per cent carbohydrates — white rice, refined flour, potatoes. The fallout runs from unstable blood sugar and continual hunger to slower metabolism and muscle loss.</p>
<h2>Food inflation has shifted to protein</h2>
<p>The price pressure is now visible in the official data. The finance ministry's Monthly Economic Report for August 2026 noted that India's food inflation is undergoing a shift in composition, with protein-rich items, processed foods and edible oils emerging as the major contributors to price pressures. Consumer Food Price Index inflation rose to 5.52 per cent in July 2026 from 5.32 per cent in June, with milk, chicken, mutton, fish, refined oil, onion and arhar/tur recording notable inflation. The report warned that persistent El Nino conditions pose downside risks to crop yields and food prices, warranting attention to pulses, oilseeds and rice.</p>
<h2>Why pulses lost favour</h2>
<p>India is the world's largest producer and consumer of pulses — yet its pulse import bill grew more than three-fold, from $1.6 billion in FY21 to a record $5.5 billion in FY25. Mint's explainer traces the disconnect to the farm: most pulses are low-productivity crops grown on marginal, rain-fed land with no irrigation, prone to drought and excess rain. And while the government declares minimum support prices, assured purchases have been low — summer-grown moong, tur and urad were recently selling at 14 to 28 per cent discounts to MSP, because imports at very low or zero duties undercut domestic growers. Yellow peas imported from Canada at zero duty sell for under Rs 3,000 per quintal, against the government's MSP of Rs 5,875.</p>
<p>Productivity tells the deeper story. A Niti Aayog report put average pulse productivity at 740 kg per hectare — far below the global average of 949 kg and the 1,800-plus kg yields of Canada and the USA. Unlike cereals, pulses saw limited yield improvement for want of high-yielding varieties, and being rain-fed, yields are highly vulnerable to climate: of 27 recorded El Nino years between 1951 and 2024, fifteen saw declines in both pulse production and acreage. The irony is that pulses are more climate-friendly than cereals — they use less water and fix nitrogen in the soil, and an Arvind Subramanian committee calculation put the net social benefit of growing tur instead of rice at over Rs 13,000 per hectare. Farmers still choose rice, because of higher yields and better prices.</p>
<h2>The policy push</h2>
<p>The government's answer is the Mission for Atmanirbharta in pulses, approved by the Cabinet on October 1 with a financial allocation of Rs 11,440 crore over six years, FY26 to FY31. The mission will develop and propagate pest-resistant, climate-resilient varieties, bring an additional 3.5 million hectares under pulses including fallow land, subsidise new processing units and post-harvest infrastructure, and — critically — assure purchase of pulses at MSP. The targets: production of 35 million tonnes by FY31, up from 25 million tonnes in FY25, and productivity of 1.13 tonnes per hectare.</p>
<p>In the near term, Reuters reported the government is considering cutting import duties on pulses after a weak monsoon. Meanwhile a major processor has authorised a Rs 100-crore programme to quadruple paneer capacity from 20 to 80 metric tonnes a day by June 2027, citing double-digit annual volume growth in retail paneer.</p>
<h2>What it means for the plate</h2>
<p>The policy push will take years to change what is grown. The immediate fix is on the plate: ThePrint's arithmetic suggests households should lean on the cheapest protein they already have. A bowl of dal a day, curd with meals, and where acceptable, eggs or lean meat — the Indian kitchen does not need imported powders or expensive foods, only better choices from foods it already cooks. For the diaspora's largely vegetarian households, the same math holds: dal and pulses stretch the protein budget farthest, and until India grows enough of them, the prices of paneer and pulses are likely to keep climbing.</p>"""

articles = [
    {
        "topic_id": "99fd1529-8862-48f5-89e8-a6dcc885ecc7",
        "headline": "Drishyam 3 Dips on Day 4 but Crosses \u20b9300 Crore Worldwide, Among 2026's Fastest",
        "subheadline": "The Ajay Devgn thriller fell sharply from its Sunday peak on its first Monday, but trade reports put its four-day global total past Rs 300 crore — the year's second-fastest Hindi film to the mark.",
        "slug": "drishyam-3-day-4-rs-300-crore-worldwide",
        "category": "entertainment",
        "vertical": "entertainment",
        "tags": ["drishyam-3", "ajay-devgn", "bollywood", "box-office", "indian-cinema"],
        "sources": [
            "https://www.herzindagi.com/movies/drishyam-3-the-conclusion-worldwide-box-office-collection-ajay-devgns-thriller-set-to-cross-300-crore-mark-in-just-4-days-article-1070077",
            "https://www.7globe.in/drishyam-3-full-movie-collection-drishyam-3-the-conclusion-box-office-collection-day-4-live-ajay-devgn-tabu-jaideep-ahlawat-prakash-raj-starrer-holds-strong-on-first-monday-eyes-rs-200-crore/",
            "http://mypresstoday.com/in/en/post/6230/355708226/drishyam-3-the-conclusion-box-office-collection-day-4-ajay-devgn-s-film-tops-300-crore-worldwide-among-fastest-films-to-reach-milestone.html",
            "https://www.addatoday.com/2026/10/drishyam-3-day-4-box-office-collection-occupancy-estimates.html",
        ],
        "diaspora_angle": "The film's Rs 61-crore three-day overseas gross shows how diaspora and Gulf audiences power Hindi franchise openings — and whether the weekday trend holds abroad will shape its final run.",
        "llm_score": 3,
        "kids_relevant": False,
        "article_type": "breaking",
        "image_url": None,
        "image_caption": "",
        "image_attribution": "",
        "body": body1,
    },
    {
        "topic_id": "d5f41bf0-c724-4466-aa6b-21168b22fa57",
        "headline": "India Funds Deep-Tech Startups Lavishly but Rarely Buys From Them",
        "subheadline": "Startups got less than 4 per cent of the Rs 5.03 lakh crore the government spent on GeM in FY26 — exposing the missing half of India's startup policy: public procurement.",
        "slug": "india-deep-tech-funding-first-customer-gap",
        "category": "technology",
        "vertical": "technology",
        "tags": ["deep-tech", "startups", "india-startups", "procurement", "gem", "idex", "rdi-fund"],
        "sources": [
            "https://yourstory.com/2026/09/india-funds-its-startups-why-wont-buy-from-them",
            "https://yourstory.com/2026/05/india-rdi-fund-first-deep-tech-startups-funding",
            "https://mlq.ai/news/india-approves-11-billion-government-fund-to-boost-deep-tech-startups/",
            "https://etedge-insights.com/trending/iit-madras-rs1000-cr-deep-tech-fund-gets-rs-450-crore-boost-backs-4-startups/",
        ],
        "diaspora_angle": "For diaspora engineers, founders and investors watching India from the US and Europe, procurement — not funding — is the variable that decides whether a deep-tech bet in India scales into a global company.",
        "llm_score": 3,
        "kids_relevant": False,
        "article_type": "breaking",
        "image_url": None,
        "image_caption": "",
        "image_attribution": "",
        "body": body2,
    },
    {
        "topic_id": "126934c8-3e31-450a-acb9-eb1872f5449c",
        "headline": "Paneer Costs Seven Times More Per Gram of Protein Than Masoor Dal",
        "subheadline": "With paneer and pulse prices climbing, ThePrint argues India must grow far more protein — while households can stretch their protein rupee by leaning on cheaper dals.",
        "slug": "paneer-pulses-protein-production-surge",
        "category": "food",
        "vertical": "food",
        "tags": ["paneer", "pulses", "protein", "food-inflation", "dals", "indian-diet"],
        "sources": [
            "https://www.youtube.com/watch?v=YHNLpgNjhC0",
            "https://www.livemint.com/industry/agriculture/india-pulses-mission-self-sufficiency-farmers-imports-production-11759911326299.html",
            "https://ymediaplus.com/indian-government-considers-cutting-pulse-import-duties-to-cool-food-prices/",
            "https://www.newkerala.com/news/a/food-inflation-composition-shifts-as-protein-rich-items-processed-273.htm",
            "https://in.edairynews.com/indian-processor-quadruples-paneer-manufacturing-footprint/",
        ],
        "diaspora_angle": "For the diaspora's largely vegetarian households, the same protein math holds at the grocery aisle: dal and pulses stretch the protein budget farthest, and until India grows enough of them, paneer and pulse prices are likely to keep climbing.",
        "llm_score": 3,
        "kids_relevant": False,
        "article_type": "breaking",
        "image_url": None,
        "image_caption": "",
        "image_attribution": "",
        "body": body3,
    },
]

for a in articles:
    a["word_count"] = wc(a["body"])
    path = f"{STATE}/v3-article-{a['topic_id']}.json"
    with open(path, "w") as f:
        json.dump(a, f, ensure_ascii=False)
    print(path, a["word_count"], "words")
