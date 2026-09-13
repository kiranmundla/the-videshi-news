#!/usr/bin/env python3
"""Stage articles 3-4 (part 2) for the 2026-09-12 21:45 writer run."""
import importlib.util, json, re, os
_spec = importlib.util.spec_from_file_location('run1', os.path.join(os.path.dirname(__file__), 'v3-articles-run1.py'))
_run1 = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(_run1)
wc, STATE = _run1.wc, _run1.STATE

ARTICLES = []

# ============ 3. Anila Baby double homicide (news) ============
ARTICLES.append({
 'topic_id': 'f79de49b-f276-4ac4-b7a4-f5f3a229d866',
 'llm_score': 3,
 'headline': 'Indian-Origin Woman Charged With Two First-Degree Murders in California Killings',
 'subheadline': 'Anila Baby, 32, allegedly killed two friends from Kerala in separate attacks about 90 minutes apart on August 28, and faces 50 years to life in prison if convicted.',
 'slug': 'anila-baby-two-first-degree-murders-california',
 'category': 'news',
 'vertical': 'news',
 'article_type': 'breaking',
 'tags': ['California', 'crime', 'San Jose', 'Milpitas', 'Kerala', 'murder', 'Santa Clara County'],
 'sources': [
   'https://www.timesnowworld.com/us-news/california-woman-anila-baby-charged-with-murder-of-two-friends-article-156137351',
   'https://www.northeastherald.in/world/indian-origin-woman-charged-with-2-murders-in-us-after-two-separate-killings',
   'https://articles.thelocalreport.in/indian-origin-woman-arrested-for-killing-2-malayali-friends-in-us/',
   'https://tezzbuzz.com/indian-origin-woman-held-for-allegedly-killing-two-friends-in-california/',
 ],
 'diaspora_angle': "The double homicide in the South Bay has shaken the Bay Area's large Malayali community, where the accused and both victims lived.",
 'image_url': None,
 'image_caption': 'The Santa Clara County courthouse in San Jose, California. Anila Baby appeared there on September 10 and is scheduled to return on November 17 to enter a plea on two first-degree murder charges.',
 'image_attribution': '',
 'body': '''<div class="key-takeaways"><ul>
<li>Anila Baby, 32, has been charged with two counts of first-degree murder in the deaths of Ann Mary Mathew, 35, and Anjana Hari, 35, in San Jose and Milpitas on August 28.</li>
<li>Prosecutors allege Mathew was strangled and stabbed in her San Jose home, and that Hari was struck by a vehicle in a Milpitas parking lot about 90 minutes later.</li>
<li>Baby faces a potential sentence of 50 years to life if convicted. She remains in custody and is due back in Santa Clara County court on November 17 to enter a plea.</li>
<li>The San Jose Police Department says the motive remains under investigation; all three women were friends who trace their roots to Kerala.</li>
</ul></div>
<p>An Indian-origin woman has been charged with two counts of first-degree murder in the killings of two friends in California's South Bay last month, in a case that has shaken the region's Malayali community.</p>
<p>Anila Baby, 32, is accused of killing Ann Mary Mathew, 35, and Anjana Hari, 35 &mdash; friends who, like her, trace their roots to Kerala &mdash; in separate attacks about 90 minutes apart on August 28, according to police and prosecutors.</p>
<h2>Two Killings, 90 Minutes Apart</h2>
<p>Investigators say the first killing occurred at Mathew's home on Linda Vista Street in San Jose. Officers responding to a report of suspicious circumstances at about 1:53 PM found Mathew's body inside the residence; she had been strangled and stabbed, prosecutors said. The San Jose Police Department's homicide unit, assisted by the Santa Clara County Crime Lab and the medical examiner's office, later ruled the death a homicide. According to Times Now World, surveillance footage from the home had been deleted during the time of the attack, but physical evidence &mdash; including sandals belonging to the suspect &mdash; was recovered at the scene.</p>
<p>Roughly 90 minutes later, authorities allege, Baby killed Hari in Milpitas, striking her with a vehicle in the parking lot of her apartment complex. Baby was arrested in Milpitas the same day and initially charged only in that killing. On September 8, the Santa Clara County District Attorney's office charged her with murder in Mathew's death as well.</p>
<h2>"Extremely Serious Charges"</h2>
<p>Deputy District Attorney Marisa McKeown described the allegations in stark terms. "Both women were mothers. They are residents of our community, and their families are suffering terribly from the ultimate question of 'Why would someone do this?'" she said, according to ABC7 News. "These are extremely serious charges. We believe that these were willful, premeditated and extremely violent crime scenes."</p>
<p>The San Jose Police Department said in a statement that "the motive and circumstances surrounding the event are still under investigation."</p>
<p>Baby made her first court appearance in Santa Clara County on September 10 and is scheduled to return on November 17, when she is expected to enter a plea, according to the Los Angeles Times. She faces two counts of first-degree murder and, if convicted, a potential sentence of 50 years to life.</p>
<h2>A Community in Shock</h2>
<p>The three women were friends, and the killings &mdash; in San Jose and Milpitas, South Bay cities less than 20 kilometers apart with large Indian-American populations &mdash; have reverberated through the Bay Area's Kerala community. Regional media report that Union Minister Suresh Gopi said efforts are underway to return the victims' bodies to Kerala, and that the Indian consulate in San Francisco is coordinating with the families.</p>
<h2>What's Next</h2>
<p>Baby remains in custody. With the November 17 hearing approaching, prosecutors and investigators continue to work on the circumstances and motive behind the killings.</p>''',
})

# ============ 4. Harleen Deol (sports) ============
ARTICLES.append({
 'topic_id': '19cca0b4-2d0d-4484-9690-5697bbffba32',
 'llm_score': 3,
 'headline': 'Harleen Deol Joins Barbados Tridents for Remainder of WCPL 2026',
 'subheadline': "The 28-year-old India batter becomes the fifth Indian in this year's Women's Caribbean Premier League, linking up with Kiran Navgire and Pooja Vastrakar for her first global franchise stint.",
 'slug': 'harleen-deol-barbados-tridents-wcpl-2026',
 'category': 'sports',
 'vertical': 'sports',
 'article_type': 'breaking',
 'tags': ['Harleen Deol', 'WCPL', 'Barbados Tridents', "women's cricket", 'T20', 'Caribbean Premier League'],
 'sources': [
   'https://www.cricinfo.com/story/india-batter-harleen-deol-joins-barbados-tridents-for-remainder-of-wcpl-1553869',
   'https://ianslive.in/just-want-to-play-freely-harleen-deol-readies-herself-for-maiden-wcpl-stint-with-tridents--20260912115836',
   'https://www.latestly.com/sports/cricket/indias-harleen-deol-joins-barbados-tridents-for-wcpl-2026-7601006.html',
   'https://xionews.com/harleen-deol-joins-barbados-tridents-for-remainder-of-2026-wcpl-season/',
 ],
 'diaspora_angle': 'A fifth Indian joins the Caribbean league, with three Indians now in the defending champions\' squad.',
 'image_url': None,
 'image_caption': 'Kensington Oval in Barbados, the venue for all matches of the 2026 Women\'s Caribbean Premier League. Harleen Deol joined the Barbados Tridents on September 11 for the remainder of the tournament.',
 'image_attribution': '',
 'body': '''<div class="key-takeaways"><ul>
<li>Harleen Deol has signed with the Barbados Tridents for the remainder of the 2026 Women's Caribbean Premier League, effective September 11.</li>
<li>The India batter becomes the fifth Indian in WCPL 2026, joining compatriots Kiran Navgire and Pooja Vastrakar in the Tridents squad for her first global franchise T20 tournament.</li>
<li>The defending champions, winners of the last three WCPL titles, opened their campaign on September 5 with a 21-run defeat to Trinbago Knight Riders.</li>
<li>Deol, 28, says she wants to "play freely": "I just want to enjoy cricket, that's it."</li>
</ul></div>
<p>India batter Harleen Deol has joined the Barbados Tridents for the remainder of the 2026 Women's Caribbean Premier League, becoming the fifth Indian cricketer to feature in the competition this season, according to Cricinfo.</p>
<p>Deol, 28, signed as the Tridents' fifth overseas player in a deal effective September 11. Because she is not currently part of the senior India or India A squads, she will be available to the franchise through the tournament, which concludes with the final on September 17. All matches are being played at Kensington Oval in Barbados.</p>
<h2>A Last-Minute Call to the Caribbean</h2>
<p>Deol's arrival came fast. "I'm with the Barbados Tridents and it's only been two days for me. Like, it was very last minute," she told IANS in a virtual interaction organized by FanCode, the tournament's official broadcaster in India. "It was a very last minute call. I think Shashank sir, from the management team, approached me and asked, 'Are you interested in playing WCPL?' I was like, 'Yeah, why not?' Because obviously, different experiences, different wickets, and different people are here."</p>
<p>The stint is Deol's first in a global franchise T20 tournament. A member of India's 2025 ODI World Cup-winning squad, she said she is treating the Caribbean as a learning experience rather than an audition.</p>
<blockquote class="pull-quote">
<p>"What I want is that I should just look to play freely, that's it. I don't think there is much difference here. It's just like, I just want to enjoy cricket, that's it."</p>
<cite>&mdash; Harleen Deol, to IANS</cite>
</blockquote>
<h2>One of Five Indians in the WCPL</h2>
<p>Deol's signing takes the Indian contingent in WCPL 2026 to five &mdash; a quarter of the 20 overseas slots across the four teams. She joins Kiran Navgire and Pooja Vastrakar in the Tridents' overseas group, while Shikha Pandey and Yastika Bhatia are representing Trinbago Knight Riders.</p>
<p>Deol has played 28 T20 internationals for India, scoring 311 runs in 20 innings at a strike rate of 92.01. Her most recent international appearance came against Australia in March 2026; her last T20I was in December 2025 against Sri Lanka. In the Women's Premier League, she has 649 runs from 28 matches at a strike rate of 115.68 for the Gujarat Giants and UP Warriorz, and she registered her maiden ODI century &mdash; 115 off 103 balls against the West Indies &mdash; in December 2024.</p>
<h2>Defending Champions Under Early Pressure</h2>
<p>The Tridents are the team to beat: they have won the last three WCPL titles, in 2023, 2024, and 2025. But their 2026 defense began with a 21-run defeat to Trinbago Knight Riders in the tournament opener on September 5 &mdash; a match in which three Indian players starred. Pandey took 3 for 17 and Bhatia struck 35 off 28 balls for the Knight Riders, while Navgire made 28 off 21 for the Tridents.</p>
<p>Deol's arrival strengthens the batting as the Tridents head into a pivotal weekend: they face the Jamaica Empress on September 12 and the Guyana Amazon Warriors on September 13, both at Kensington Oval.</p>
<h2>What's Next</h2>
<p>With the final scheduled for September 17, Deol has just over a week to make her mark. A strong WCPL showing would be a timely reminder to the national selectors ahead of a busy home season.</p>''',
})

for a in ARTICLES:
    a['word_count'] = wc(a['body'])
    fn = os.path.join(STATE, 'v3-article-%s.json' % a['topic_id'])
    with open(fn, 'w') as f:
        json.dump(a, f, indent=1, ensure_ascii=False)
    print('%s | slug=%s | words=%d' % (a['topic_id'], a['slug'], a['word_count']))
