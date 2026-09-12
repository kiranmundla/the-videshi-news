#!/usr/bin/env python3
"""Insert 4 V3 articles for batch C. Prints JSON lines: slug, id, topic_id."""
import json, os, re, subprocess
from datetime import datetime, timezone

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def curl(method, path, data=None, params=""):
    cmd = ["curl", "-sS", "-X", method,
           f"{SUPABASE_URL}/rest/v1/{path}{params}",
           "-H", f"apikey: {KEY}",
           "-H", f"Authorization: Bearer {KEY}",
           "-H", "Content-Type: application/json"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    if method == "POST":
        cmd += ["-H", "Prefer: return=representation"]
    elif method == "PATCH":
        cmd += ["-H", "Prefer: return=minimal"]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out.stdout

def word_count(html):
    text = re.sub(r"<[^>]+>", " ", html)
    return len([w for w in text.split() if w.strip()])

now = datetime.now(timezone.utc).isoformat()

articles = []

# --- Article 1: Swara Bhasker (entertainment) ---
a1_body = """<div class="key-takeaways"><ul><li>Swara Bhasker says Salman Khan personally mentored her during 2015's <em>Prem Ratan Dhan Payo</em>, coaching her on camera craft, styling and "the psychology of stardom."</li><li>The actor has repeatedly argued that streaming has "democratised creativity and stardom," opening space for new stories and performers outside the box-office system.</li><li>Bhasker attributes Bollywood's box-office slump to an economic slowdown, COVID-19 and the rise of OTT content — not only to boycott campaigns.</li><li>Her outspoken assessments span the Khans' three-decade dominance, the industry's star machinery and its shifting audience tastes.</li></ul></div>
<p>Swara Bhasker has never treated celebrity as a gag order. In a run of candid interviews — from trade conversations to a recent sit-down that has reignited debate about where Hindi cinema stands — the actor has laid out an unusually blunt account of Bollywood's evolution: the three-decade reign of the Khans, the arrival of streaming as a creative equaliser and an industry being forced to rethink its storytelling.</p>
<h2>The Khans and the star machine</h2>
<p>Bhasker entered Hindi cinema in 2009's <em>Madholal Keep Walking</em> and broke through with <em>Tanu Weds Manu</em> (2011), <em>Raanjhanaa</em> (2013) and <em>Nil Battey Sannata</em> (2016). She has straddled two worlds: big commercial titles such as <em>Prem Ratan Dhan Payo</em> (2015) and <em>Veere Di Wedding</em> (2018), and fiercely independent cinema.</p>
<p>On the sets of the 2015 Sooraj Barjatya blockbuster, where she played Salman Khan's sister, the superstar took an unexpected interest in her trajectory. "What surprised me most was how invested Salman was in transforming me," Bhasker said in a recent interview. "He wasn't just focused on his own performance — he was actively thinking about my career trajectory and how to position me as a leading lady." Khan coached her on camera angles and lighting specific to heroines, carrying traditional outfits, screen presence in large-scale productions and, as she put it, "the psychology of stardom."</p>
<blockquote class="pull-quote"><p>"Working with Salman in a Sooraj Barjatya film was like a masterclass in mainstream cinema."</p><cite>— Swara Bhasker</cite></blockquote>
<p>Her reading of the industry's star system has long circled around Shah Rukh Khan, Salman Khan and Aamir Khan — the trio whose combined box-office dominance defined three decades of Hindi film. "An actor can become a star, but to retain that position like SRK, Salman or Aamir for 25 years is difficult," she said at a 2017 industry event. Nine years later, trade analysts say Hindi cinema still has not built a successor generation to replace them.</p>
<h2>OTT as the great leveller</h2>
<p>Bhasker's most sustained argument concerns streaming. In a 2020 interview with Bollywood Hungama's Subhash K. Jha, she said: "OTT platforms have not only changed content by opening up a space for new stories, new characters and new ideas to be accepted, they have also democratised content. They've democratised creativity and by giving a platform to talented new and old actors OTT has democratised stardom."</p>
<p>She cautioned that the old order had not finished adapting: "It is yet to be seen how the traditional box office determined ecosystem of theatrical cinema will readjust to this change." Six years on, that readjustment is still underway, with 2026 box-office data showing theatrical revenues increasingly concentrated in a handful of tentpoles.</p>
<h2>The boycott debate and the slump</h2>
<p>When India Today asked her about the 'Boycott Bollywood' campaigns that plagued the industry in the early 2020s, Bhasker called the attempts to bring the industry down "petty and disgusting," pointing out that it provides livelihoods to thousands of workers. Quoting director Anurag Kashyap, she said the country's economic slump explained part of the downturn — along with COVID-19 and the arrival of OTT content drawing audiences away from theatres.</p>
<p>"After the unfortunate and tragic suicide of Sushant, Bollywood has been painted as a really dark place, that is only about drugs and alcohol and sex," she said, arguing that perception had done as much damage as any organised campaign.</p>
<h2>A reckoning with her own films</h2>
<p>Bhasker has also turned her candour on her own filmography. In a 2025 conversation with Hauterrfly, she revisited the long-running controversy over <em>Raanjhanaa</em> (2013), widely criticised for glorifying stalking. She admitted she had not recognised the problem while making it: her first brush with the criticism came when a journalist raised it at the trailer launch.</p>
<p>She used the moment to diagnose a broader pattern in Hindi hits: the suffering male protagonist. "India is full of 'naskatuye aashiq'," she said. "Mardon ki bechargi se zyada profitable art mein kuch nahi hai" — nothing is more profitable in art than stories about victimised men. She cited <em>Raanjhanaa</em>, <em>Devdas</em> and 2025's romantic drama <em>Saiyaara</em> as examples of the trope.</p>
<blockquote class="pull-quote"><p>"OTT platforms have not only changed content by opening up a space for new stories, new characters and new ideas to be accepted, they have also democratised content."</p><cite>— Swara Bhasker, on streaming</cite></blockquote>
<h2>Impact and analysis</h2>
<p>Bhasker's position — commercial insider and outspoken outsider — makes her a useful barometer for the industry. Her remarks connect the threads of the current moment: a concentrated star system struggling to produce new headliners, the streaming correction that rewrote distribution economics, and audiences migrating toward southern-language cinema and Hollywood spectacles. She has also been open about the personal cost of her outspokenness, saying producers have told her she carries "nuisance value" and that her activism during the CAA-NRC protests cost her work.</p>
<h2>Diaspora angle</h2>
<p>For diaspora audiences, whose Hindi-film viewing now runs overwhelmingly through streaming rather than overseas theatres, Bhasker's argument that OTT has "democratised stardom" describes how NRIs already experience Bollywood — with smaller films and regional titles a click away from the tentpoles.</p>
<h2>What's next</h2>
<p>Bhasker is currently seen on the reality show <em>Pati Patni Aur Panga</em>. Whether her political candour continues to limit her casting — a tradeoff she has described as "conscious" — will test how much room the industry genuinely has for dissent.</p>
"""

articles.append({
    "headline": "Swara Bhasker on Bollywood's Evolution: The Khans, OTT and the Industry's Reckoning",
    "subheadline": "In a series of candid interviews, the actor weighs in on Salman Khan's mentorship, streaming's levelling of stardom, the boycott-era slump and the industry's storytelling habits.",
    "body": a1_body,
    "slug": "swara-bhasker-bollywood-evolution-khans-ott-industry-reckoning",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": ["Swara Bhasker", "Bollywood", "Salman Khan", "OTT", "Interview"],
    "sources": [
        {"name": "Bharat Horizon", "url": "https://bharathorizon.com/entertainment/bollywood/swara-bhasker-salman-khan-mentored-me-to-be-heroine.html"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/features/ott-democratised-creativity-stardom-swara-bhaskar/"},
        {"name": "OTTplay", "url": "https://www.ottplay.com/news/swara-bhasker-on-boycott-bollywood-trend-industry-was-painted-as-a-dark-place-after-sushant-singh-rajputs-death/21385d498f723"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/news/features/swara-bhasker-calls-bollywoods-victimised-men-trope-cites-raanjhanaa-devdas-saiyaara-examples-india-full-naskatuye-aashiq/"}
    ],
    "diaspora_angle": "Diaspora audiences now watch Hindi cinema primarily on streaming, making Bhasker's argument that OTT has 'democratised stardom' a direct description of how NRIs experience Bollywood.",
    "topic_id": "e25b87b6-18d6-4b75-b3c0-73e36130ebaf",
    "llm_score": 3,
})

# --- Article 2: Bollywood's shrinking share (entertainment) ---
a2_body = """<div class="key-takeaways"><ul><li>India's domestic box office reached ₹8,147 crore through July 2026, up 13% year on year — but Hindi cinema's share has slipped below 40% for the first time this year, to 38%.</li><li>Hollywood's share hit a record 17%, beating its 2019 peak of 15%; <em>Spider-Man: Brand New Day</em> crossed ₹500 crore to become the highest-grossing international film ever in India.</li><li>Telugu (18%), Tamil (13%) and Malayalam (7%) cinema now claim a combined 38% of domestic revenue — matching Hindi's entire share.</li><li>Box-office wealth is concentrated at the top: July's four biggest releases captured 81% of the month's collections, with <em>Spider-Man</em> alone taking 40%.</li></ul></div>
<p>On paper, Indian cinema is enjoying one of its strongest commercial runs since the pandemic. Through the first seven months of 2026, cumulative gross domestic collections reached ₹8,147 crore — up 13% compared with the same period in 2025, according to data from Ormax Media, reported by CNBC TV18. July alone added ₹1,582 crore, the second-highest-grossing month of the year so far.</p>
<p>But beneath the record topline, the money is moving away from Mumbai. For the first time in 2026, Hindi cinema's share of the domestic box office has slipped below 40%, settling at 38% through July — down sharply from the 44% it commanded at the end of June. The ground it lost has been captured by Hollywood spectacles and consistent regional blockbusters.</p>
<h2>Hollywood's record run</h2>
<p>The primary disruptor in 2026 has been international cinema, which expanded its domestic footprint to a record-high 17% share of total Indian box-office revenue through July. Hollywood's previous annual best stood at 15% in 2019.</p>
<p>Driving the surge was a historic performance by <em>Spider-Man: Brand New Day</em>, which grossed over ₹500 crore — surpassing <em>Avatar: The Way of Water</em> to become the highest-grossing international film of all time in India, and the second-highest-grossing film of 2026 overall. It trails only <em>Dhurandhar: The Revenge</em>, which crossed the ₹1,000 crore mark domestically and became the highest-grossing Hindi film of all time, per Ormax data cited by exchange4media. Coupled with Christopher Nolan's <em>The Odyssey</em> (₹220 crore), international films generated over ₹1,424 crore between January and July — putting Hollywood on track to eclipse its pre-pandemic 2019 revenue record of ₹1,595 crore well before the year-end release of <em>Avengers: Doomsday</em>.</p>
<h2>The regional surge</h2>
<p>Telugu cinema currently commands an 18% share of the domestic box office, Tamil cinema holds 13%, and Malayalam and other regional languages account for 7% each — a combined 38%, equal to Hindi's entire share.</p>
<p>The shift shows up in the year's top titles. Across the top 10 domestic releases of 2026 through July, Hindi cinema accounts for four — <em>Dhurandhar: The Revenge</em>, <em>Border 2</em>, <em>Bhooth Bangla</em> and <em>Dhamaal 4</em> — while Telugu (<em>Peddi</em>, <em>Mana Shankara Vara Prasad Garu</em>), Tamil (<em>Jana Nayagan</em>, <em>Karuppu</em>) and Hollywood (<em>Spider-Man</em>, <em>The Odyssey</em>) claim two spots each. Ormax's April data had Hindi at a 50% share; by July that lead had evaporated.</p>
<h2>A two-tentpole economy</h2>
<p>The strong headline hides a fragile structure. Ashish Misra, head of commercialisation at Cinepolis India, notes that Q1 2026's ₹3,440 crore — 17% higher than Q1 2025 — was shaped by "two large tentpoles at the bookends," with January closing at ₹1,327 crore and March at ₹1,690 crore on the strength of <em>Dhurandhar: The Revenge</em>, while February, at under ₹500 crore, was the softest month since February 2023.</p>
<blockquote class="pull-quote"><p>"The headline is strong, the curve underneath it is still uneven. That distinction matters because it tells us where the work still is."</p><cite>— Ashish Misra, Head of Commercialisation, Cinepolis India</cite></blockquote>
<p>Misra identifies the missing middle as the industry's real task: "The piece that still needs building is the depth of mid-budget, content-led Indian films that hold the weeks in between the big releases. A genuine year-round box office is not made of five or six tentpoles spread across the calendar. It is made of those tentpoles plus a steady flow of films in the ₹50 to ₹200 crore band that keep occupancy healthy week on week."</p>
<p>July illustrates the concentration: the top four releases — <em>Spider-Man: Brand New Day</em>, the Tamil blockbuster <em>Jana Nayagan</em> (₹230 crore), <em>The Odyssey</em> (₹220 crore) and the Hindi comedy <em>Dhamaal 4</em> (₹197 crore) — accounted for 81% of the month's receipts, with <em>Spider-Man</em> generating 40% on its own.</p>
<h2>Impact and analysis</h2>
<p>The structural squeeze has two engines. Hollywood franchises now open day-and-date with massive dubbed footprints and premium-format pricing, pulling the top end of the audience. Regional cinema, meanwhile, is eating the middle: it recovered faster from the pandemic, takes bigger creative risks and now releases pan-India with Hindi dubs as a matter of course. PVR INOX reported a net profit of ₹186 crore for the January-March FY26 quarter, but the gains are pooling at the exhibition majors and the tentpole producers.</p>
<p>For Bollywood, the danger is not a bad year — 2026 is, in aggregate, a record one — but a shrinking claim on it. When a single Hollywood title can outgross every Hindi release of the month except the year's biggest, the centre of gravity has moved.</p>
<h2>Diaspora angle</h2>
<p>Overseas, diaspora audiences mirror the trend: <em>Spider-Man: Brand New Day</em> also reclaimed the No. 1 global box-office spot from <em>The Odyssey</em>, while Telugu and Tamil blockbusters continue to fill North American multiplexes — the same screens where Hindi tentpoles once had the weekend to themselves.</p>
<h2>What's next</h2>
<p>The second half of 2026 is packed: <em>Ramayana: Part 1</em>, <em>King</em>, <em>Toxic</em>, <em>Fauzi</em>, <em>Jailer 2</em> and <em>Avengers: Doomsday</em> are all on the calendar. Ormax's first-half report put January-June at ₹6,398 crore — the strongest post-pandemic first half — and said 100 crore annual footfalls remain achievable. Whether Hindi cinema reclaims share will depend on the festival slate, not the record books.</p>
"""

articles.append({
    "headline": "Hollywood and Regional Hits Squeeze Bollywood's Share Below 40 Percent in 2026",
    "subheadline": "India's box office is headed for a record year, but Ormax data shows Hindi cinema ceding ground to a ₹500-crore Spider-Man and surging Telugu and Tamil releases.",
    "body": a2_body,
    "slug": "hollywood-regional-hits-squeeze-bollywood-share-below-40-percent",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": ["Bollywood", "Box Office", "Hollywood", "Regional Cinema", "Ormax"],
    "sources": [
        {"name": "CNBC TV18", "url": "https://trends.glance.com/story/articles/entertainment/in/en/cnbc-tv18/s-8a90979888-2e589b6d-5fa0-54a0-b63a-7723847d6e08"},
        {"name": "exchange4media", "url": "https://www.exchange4media.com/media-others-news/is-box-office-shift-turning-cinema-into-a-365-day-advertising-platform-154756.html"},
        {"name": "Storyboard18", "url": "https://www.storyboard18.com/how-it-works/india-box-office-collects-rs-787-crore-in-april-2026-revenues-still-15-ahead-of-last-year-ormax-report-99857.htm"}
    ],
    "diaspora_angle": "Diaspora moviegoers mirror the shift, filling overseas multiplexes for Spider-Man and Telugu/Tamil blockbusters that now share screens once dominated by Hindi tentpoles.",
    "topic_id": "311e356f-8e5f-474e-be9a-99fd6a6a4201",
    "llm_score": 3,
})

# --- Article 3: Bollywood's fierce female cops (entertainment) ---
a3_body = """<div class="key-takeaways"><ul><li>Rediff film critic Sukanya Verma spotlights Hindi cinema's new wave of women in uniform, from Kareena Kapoor Khan's "cop who wears lipstick" in <em>Daayra</em> to Rani Mukerji's Shivani Shivaji Roy in the <em>Mardaani</em> films.</li><li>Rani Mukerji's <em>Mardaani 3</em> closed its 2026 theatrical run at about ₹77 crore — the franchise's best — completing the first hattrick of hits for a female-cop series in 113 years of Hindi cinema.</li><li>Streaming drove the shift: <em>Delhi Crime</em>, <em>Dahaad</em>, <em>Aranyak</em>, <em>Kohrra</em> and <em>Brown</em> gave women investigators sustained screen time after Netflix's 2016 India entry rewrote the economics of risk.</li><li>Actresses say the draw is complexity, not the uniform: flawed, middle-aged protagonists whose vulnerability and competence coexist.</li></ul></div>
<p>In early 2026, Rani Mukerji's <em>Mardaani 3</em> closed its theatrical run earning about ₹77 crore — the highest-grossing film in the 12-year-old franchise's history. According to Bollywood Hungama, it made the <em>Mardaani</em> series the only female-cop franchise to succeed in 113 years of Hindi cinema, landing an unprecedented hattrick of hits. For Rediff film critic Sukanya Verma, the milestone is part of a wider turn: from Kareena Kapoor Khan's "cop who wears lipstick" in <em>Daayra</em> to Mukerji's relentless Shivani Shivaji Roy, Bollywood's portrayals of female police officers have grown more powerful — and more nuanced.</p>
<h2>A long history of one-offs</h2>
<p>Women in uniform have appeared in Indian cinema since at least the 1980s. They just never stayed long enough to change anything. Hema Malini wore the khaki in <em>Andhaa Kaanoon</em> (1983), a courtroom drama built around maternal fury rather than investigative procedure. Rekha headlined <em>Phool Bane Angaray</em> (1991), playing an officer transformed from grieving widow into seeker of justice.</p>
<p>In the South, Vijayashanti built something more sustained in Telugu cinema through the late 1980s and 1990s — a whole identity as an action heroine and police officer that earned her the nickname "Lady Amitabh." Tabu turned the investigating officer into a morally complicated figure in the <em>Drishyam</em> franchise. Priyanka Chopra Jonas played a district superintendent in <em>Jai Gangaajal</em> (2016), leading from the front against land-grabbing politicians in rural Bihar. Each portrayal was remarkable; each remained an island.</p>
<p>The reason was economic. As Forbes India noted, Indian cinema's formula was organised around a simple equation: audiences came for the male star. From Amitabh Bachchan in <em>Zanjeer</em> to Om Puri in <em>Ardh Satya</em>, Aamir Khan in <em>Sarfarosh</em> and Ajay Devgn in <em>Singham</em>, the cop was imagined as a masculine force imposing order through brute strength. "What ends up happening," says <em>Brown</em> director Abhinay Deo, "is that even if a woman-centric film does well, there is no comparison to a man-centric film doing well. We're talking about ticket sales and the film scenario, until OTT came along."</p>
<h2>The OTT cascade</h2>
<p>The advent of Netflix in India in 2016, followed by JioHotstar, ZEE5, SonyLIV and Prime Video, changed the economic models that had limited storytelling to familiar tropes. "Prime time has changed to my time, and OTT has brought about that change," says Devendra Deshpande, CEO of Friday Filmworks. "The minute you free yourself from that chained scenario and say, 'I don't have to worry about box office anymore', it opens doors and windows."</p>
<p><em>Delhi Crime</em> was the proof of concept. Shefali Shah's calm, razor-sharp DCP Vartika Chaturvedi, leading the investigation into the 2012 Nirbhaya case, won India its first International Emmy for Best Drama Series in 2020; a third season streamed in November 2025, and the show became the most-watched in 10 countries on Netflix. "Even today, when I wear that uniform, I get goosebumps," Shah says. "Every single time I wear it, I stand differently."</p>
<blockquote class="pull-quote"><p>"Even today, when I wear that uniform, I get goosebumps. Every single time I wear it, I stand differently."</p><cite>— Shefali Shah, on playing DCP Vartika Chaturvedi in <em>Delhi Crime</em></cite></blockquote>
<p>The cascade that followed was quick. Sonakshi Sinha's Anjali Bhaati in <em>Dahaad</em> placed a small-town Rajasthani officer at the centre of a serial-killer investigation tangled with caste, gender and institutional prejudice. Raveena Tandon's Kasturi Dogra navigated a murder mystery in <em>Aranyak</em> while juggling family pressures and workplace scepticism. Bhumi Pednekkar's Rita Ferreira in <em>Daldal</em> brought a messy, morally conflicted protagonist to the screen; Mona Singh's Baljit Kaur gave Punjabi crime drama its most textured female lead in <em>Kohrra</em>; Kareena Kapoor Khan's Jasmeet Kaur Bedi carried a cold-case investigation in England in <em>The Buckingham Murders</em>; Deepika Padukone entered Rohit Shetty's cop universe as Shakti Shetty in <em>Singham Again</em>. In June 2026, Karisma Kapoor returned to the screen in <em>Brown</em> as Rita Brown, a recovering alcoholic detective with the Kolkata police — flawed, unglamorous, fiercely complex.</p>
<h2>Vulnerability as the point</h2>
<p>What connects these women is not the job title but a proposition that was once foreign to Indian mainstream storytelling: their vulnerability and competence coexist. "Portraying authority on screen isn't about volume or aggression. It's about stillness, conviction and knowing exactly when to push and when to hold back," Sinha says of Anjali Bhaati, whose authority is "constantly challenged, not just externally but layered with caste, gender and the system she operates within."</p>
<p>"Perfection is no longer interesting," Sinha adds. "With Anjali, her flaws and vulnerabilities don't take away from her strength, they define it. She gets things wrong, she doubts herself, she's affected by what she sees, and yet she shows up and does the job."</p>
<p>Rasika Dugal, who plays ACP Neeti Singh in <em>Delhi Crime</em>, extends the point beyond gender: "There can be a lot of power with a soft exterior as well." Her character is petite, softly spoken and consistently underestimated — a deliberate rejection of the idea that women in control must behave in a masculine fashion.</p>
<h2>Impact and analysis</h2>
<p>The creative change had to survive the commercial one. <em>Mardaani 3</em> is the strongest evidence it did: Mukerji's Shivani Roy was, when the first film released in 2014, a rarity — a mainstream Hindi action heroine, neither young nor glamorous, carrying the film's moral and commercial weight alone. The franchise survived a six-year gap between its second and third instalments and returned in 2026 to its best numbers yet. Mukerji describes the character as a salute to real women in uniform "who are not celebrated as much as they need to be celebrated."</p>
<p>The fault line now runs between platforms. As Pednekkar puts it: "On digital platforms there are a lot of female-first narratives, which is great. But theatrically" — the sentence trails off into the industry's unresolved question of whether the faith in these stories holds when box-office pressure returns.</p>
<h2>Diaspora angle</h2>
<p>Streaming has made these performances global by default: <em>Delhi Crime</em> topped charts in 10 countries, and NRI audiences have discovered Indian crime drama on the same platforms that carry their Bollywood tentpoles — a second front for Indian storytelling abroad.</p>
<h2>What's next</h2>
<p>Rohit Shetty has confirmed a standalone film for Deepika Padukone's Lady Singham, and Kareena Kapoor Khan's <em>Daayra</em> — where she plays the "cop who wears lipstick" — will test whether the theatrical audience for women-led crime stories keeps growing.</p>
"""

articles.append({
    "headline": "From Mardaani to Delhi Crime: Hindi Cinema's Women Cops Take Charge",
    "subheadline": "Rani Mukerji's franchise completed an unprecedented hattrick of hits, while streaming turned Shefali Shah, Sonakshi Sinha and Raveena Tandon into television's most compelling investigators.",
    "body": a3_body,
    "slug": "mardaani-delhi-crime-hindi-cinema-women-cops-take-charge",
    "category": "entertainment",
    "vertical": "entertainment",
    "tags": ["Rani Mukerji", "Mardaani", "Delhi Crime", "Bollywood", "Women in Cinema"],
    "sources": [
        {"name": "Rediff (via Muck Rack)", "url": "https://muckrack.com/sukanya-verma"},
        {"name": "Bollywood Hungama", "url": "https://www.bollywoodhungama.com/amp/news/box-office-special-features/mardaani-makes-history-female-cop-franchise-succeed-113-years-hindi-cinema-lands-unprecedented-hattrick-hits/"},
        {"name": "Forbes India", "url": "https://www.forbesindia.com/article/life/uniform-roles-why-are-more-women-actors-playing-on-screen-cops/2995321/1"}
    ],
    "diaspora_angle": "Streaming made these performances global by default — Delhi Crime topped charts in 10 countries, giving NRI audiences a second front of Indian storytelling beyond Bollywood tentpoles.",
    "topic_id": "44377b7d-397d-4df8-87de-03a32bec7796",
    "llm_score": 3,
})

# --- Article 4: Krystle D'Souza home tour (lifestyle-health) ---
a4_body = """<div class="key-takeaways"><ul><li>Krystle D'Souza gave filmmaker Farah Khan a tour of her Lokhandwala, Andheri West apartment in a YouTube video released on September 7.</li><li>The three-and-a-half-bedroom high-rise blends modern and Parisian-inspired interiors: beige tones, wooden textures, fluted panelling and high-gloss flooring, all designed by D'Souza herself.</li><li>Standout details include a Sabyasachi floral wallpaper — about ₹35,000 per roll — in the bedroom, and a "bedroom-sized" glam room with an orange couch, stone wall and a neon sign reading "Everything You Can Imagine Is Real."</li><li>D'Souza, who grew up in a 700 sq ft Sion home shared with seven family members, bought the apartment during the pandemic.</li></ul></div>
<p>Actor Krystle D'Souza has opened the doors of her Mumbai home. In a YouTube video released on September 7, the recent <em>The Traitors</em> season 2 winner walked filmmaker Farah Khan through her Lokhandwala, Andheri West apartment — a space she bought during the pandemic and designed almost entirely herself, in a blend of modern and Parisian-inspired interiors.</p>
<h2>A warm, neutral palette</h2>
<p>The high-rise apartment runs on a warm, neutral palette: beige tones, wooden textures and sleek high-gloss flooring. The open-plan living and dining area follows the home's understated aesthetic, with vertical fluted wooden panelling and integrated warm lighting adding depth. Large floor-to-ceiling glass doors bring in natural light and open onto a balcony fitted with a wooden bench, soft pastel cushions and handcrafted macramé wall decor.</p>
<p>Nearby, the dining area centres on a large wooden table paired with chairs, complemented by wall paintings and framed artwork. A built-in display unit holds D'Souza's acting awards, books and travel souvenirs, while the uncluttered floor space leaves room for entertaining. "I am loving this space," Farah said during the tour.</p>
<h2>From 700 sq ft to a high-rise</h2>
<p>The tour turned personal when D'Souza recalled the much smaller home she grew up in. "It was a one-bedroom hall… I think some 700 square feet," she said, explaining that her mother, father, grandmother, uncle, aunt, brother and she all lived together in Sion. Farah related immediately: "We also had a small 500-square-foot house like this. We all used to stay there."</p>
<p>When Farah asked whether the apartment was genuinely hers — "Yeh tera asli ghar hai? No rent, nothing?" — D'Souza replied that she had worked hard for it: "Khoon paseena ek karke banaaya hai. This is my house, my own house, not rented."</p>
<h2>A New York-style bedroom</h2>
<p>The same muted aesthetic continues into the bedroom, which features a light beige tufted headboard against a floral wallpaper accent wall and a large window with city views. Stepping in, Farah joked: "Oh my, Krystle. We are in a bedroom in New York. You can see the Empire State Building from here."</p>
<p>The room's standout feature is its Sabyasachi floral wallpaper, priced at around ₹35,000 per roll — a luxe, statement touch in an otherwise muted space. The apartment also includes a dedicated walk-in wardrobe, neatly organised with designer clothes and handbags, for the actor, who openly admits her love for fashion.</p>
<p>"I love bags," D'Souza said, pointing out pieces she uses regularly — including designer bags she takes out for everyday outings. Farah quipped: "Designer bags are being used for everyday, guys. I also should have done 2-3 item songs." D'Souza clarified: "This is just because of television, not item songs."</p>
<blockquote class="pull-quote"><p>"I live alone, what would I do with a three-and-a-half-bedroom?"</p><cite>— Krystle D'Souza</cite></blockquote>
<h2>The glam room</h2>
<p>The most personal space in the home is the dedicated vanity and glam room — the one room that breaks from the neutral tones. It features a bold orange couch against a stone backdrop and an illuminated neon sign reading "Everything You Can Imagine Is Real."</p>
<p>Farah was struck by the size of the space, describing it as almost "bedroom-sized." "I am a makeup junkie," D'Souza said, explaining that doing her own makeup is something she genuinely enjoys and finds therapeutic. She added that she is planning a second vanity to accommodate her growing collection: "I have lots and lots."</p>
<h2>Diaspora angle</h2>
<p>Celebrity home tours are appointment viewing for design-minded NRIs weighing a Mumbai pied-à-terre or planning their own interiors — and D'Souza's mix of Parisian detailing, Sabyasachi accents and a dedicated vanity space offers a template that translates well to diaspora homes too.</p>
<h2>What's next</h2>
<p>D'Souza, whose recent win on <em>The Traitors</em> season 2 put her back in the spotlight, hinted the apartment is still evolving — with another vanity in the works to house her expanding beauty collection.</p>
"""

articles.append({
    "headline": "Inside Krystle D'Souza's Mumbai Home: Parisian Chic, a Glam Room and Sabyasachi Walls",
    "subheadline": "The Traitors season 2 winner gave Farah Khan a tour of her self-designed Lokhandwala apartment — from a ₹35,000-a-roll Sabyasachi bedroom wall to a bedroom-sized vanity room.",
    "body": a4_body,
    "slug": "krystle-dsouza-mumbai-home-parisian-glam-room-sabyasachi-walls",
    "category": "lifestyle-health",
    "vertical": "lifestyle-health",
    "tags": ["Krystle D'Souza", "Farah Khan", "Home Tour", "Interior Design", "Mumbai"],
    "sources": [
        {"name": "Hindustan Times", "url": "https://www.hindustantimes.com/lifestyle/art-culture/step-inside-krystle-d-souza-s-mumbai-home-with-parisian-inspired-decor-bedroom-sized-glam-room-and-sabyasachi-wallpaper-101788849152987.html"},
        {"name": "Asia Today", "url": "https://asiatoday.co/2026/09/08/inside-krystle-dsouzas-mumbai-home-new-york-inspired-bedroom-glam-room-sabyasachi-wallpaper-and-more/"}
    ],
    "diaspora_angle": "For design-minded NRIs, the tour offers a template — Parisian detailing, Sabyasachi accents and a dedicated vanity space that translate well to diaspora homes.",
    "topic_id": "0c535473-1986-42b8-b863-308c0d12801c",
    "llm_score": 3,
})


# --- Insert + topic update ---
results = []
for a in articles:
    slug = a["slug"]
    # uniqueness check
    existing = json.loads(curl("GET", "p2_articles", params=f"?select=id&slug=eq.{slug}"))
    if existing:
        print(json.dumps({"slug": slug, "skipped": "duplicate slug"}))
        continue
    payload = {
        "headline": a["headline"],
        "subheadline": a["subheadline"],
        "body": a["body"],
        "slug": slug,
        "category": a["category"],
        "vertical": a["vertical"],
        "tags": a["tags"],
        "sources": a["sources"],
        "image_url": None,
        "image_caption": None,
        "image_attribution": None,
        "word_count": word_count(a["body"]),
        "diaspora_angle": a["diaspora_angle"],
        "topic_id": a["topic_id"],
        "llm_score": a["llm_score"],
        "published_at": now,
        "article_type": "breaking",
        "status": "published",
    }
    resp = json.loads(curl("POST", "p2_articles", data=payload))
    art = resp[0] if isinstance(resp, list) and resp else {}
    aid = art.get("id")
    print(json.dumps({"slug": slug, "id": aid, "topic_id": a["topic_id"], "word_count": word_count(a["body"])}))
    if aid:
        curl("PATCH", "p2_topics", data={"status": "published", "last_article_id": aid}, params=f"?id=eq.{a['topic_id']}")
        print(json.dumps({"topic": a["topic_id"], "updated": True}))
