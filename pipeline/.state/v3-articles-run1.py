#!/usr/bin/env python3
"""Stage V3 article JSONs for the 2026-09-12 21:45 writer run."""
import json, re, os

STATE = os.path.expanduser('~/workspace/the-videshi-news/pipeline/.state')

def wc(html):
    return len(re.sub(r'<[^>]+>', ' ', html).split())

ARTICLES = []

# ============ 1. Dr. Mukul Arya (nri-world) ============
ARTICLES.append({
 'topic_id': 'ff118115-1256-4b79-9cc2-817184ffa953',
 'llm_score': 4,
 'headline': 'Indian-American Gastroenterologist Dr. Mukul Arya to Receive Global Healthcare Leadership Award',
 'subheadline': "The White Plains Hospital director will accept the inaugural Global Healthcare Leader of the Year honor at Worldwide Community First Responder's 15th anniversary gala in Nyack on September 19.",
 'slug': 'dr-mukul-arya-global-healthcare-leader-award',
 'category': 'nri-world',
 'vertical': 'nri-world',
 'article_type': 'breaking',
 'tags': ['Indian-American', 'Dr. Mukul Arya', 'healthcare', 'gastroenterology', 'White Plains Hospital', 'WCFR', 'Nyack'],
 'sources': [
   'https://theindianeye.com/2026/09/12/indian-american-physician-dr-mukul-arya-to-receive-global-healthcare-leader-of-the-year-award/',
   'https://healthmatters.wphospital.org/news/white-plains-hospital-welcomes-dr-mukul-arya-as-director-of-advanced-gastroenterology/',
   'https://www.beckersasc.com/gastroenterology-and-endoscopy/white-plains-hospital-appoints-dr-mukul-arya-as-advanced-gi-director/',
 ],
 'diaspora_angle': 'An Indian-American physician and AAPI chapter founder receives a major healthcare leadership honor in the New York medical community.',
 'image_url': None,
 'image_caption': 'Dr. Mukul Arya, a board-certified gastroenterologist at White Plains Hospital. He will receive the inaugural Global Healthcare Leader of the Year Award at Worldwide Community First Responder\'s gala in Nyack on September 19.',
 'image_attribution': '',
 'body': '''<div class="key-takeaways"><ul>
<li>Worldwide Community First Responder will present its inaugural Global Healthcare Leader of the Year Award to Dr. Mukul Arya on September 19, 2026.</li>
<li>The White Plains Hospital gastroenterologist is being recognized for clinical excellence, healthcare leadership, and community impact.</li>
<li>The award will be presented during WCFR's 15th anniversary and fundraising gala, from 7:00 to 11:00 PM at Hotel Nyack&ndash;JDV by Hyatt in Nyack, New York.</li>
<li>Arya recently completed the Harvard Medical School Global Healthcare Leaders Program and directs advanced gastroenterology at White Plains Hospital.</li>
</ul></div>
<p>Worldwide Community First Responder, Inc. will honor Indian-American gastroenterologist Dr. Mukul Arya with its inaugural Global Healthcare Leader of the Year Award at the organization's 15th anniversary and fundraising gala later this month, according to The Indian EYE.</p>
<p>The award will be presented on Saturday, September 19, from 7:00 PM to 11:00 PM at Hotel Nyack&ndash;JDV by Hyatt in Nyack, New York. The organization said Arya is being recognized for his professional excellence, commitment to advancing healthcare, and dedication to creating a positive impact within the communities he serves.</p>
<h2>A First for the Organization</h2>
<p>The Global Healthcare Leader of the Year Award is a new honor for Worldwide Community First Responder, a nonprofit whose mission centers on preventing deaths worldwide through education and training. Arya will be its first recipient.</p>
<blockquote class="pull-quote">
<p>"Dr. Arya exemplifies the visionary leadership, compassion, and global perspective needed to strengthen healthcare systems and improve lives. We are proud to recognize him as WCFR's first Global Healthcare Leader of the Year."</p>
<cite>&mdash; Dr. Jacqueline Cassagnol, Founder and President, Worldwide Community First Responder</cite>
</blockquote>
<p>The award will be presented by restaurateur and entrepreneur Roni Mazumdar, the organization said. The gala's premier sponsors are the Arya Family Foundation and Unapologetic Foods, whose support will help WCFR continue its education and training mission. The evening is expected to bring together healthcare professionals, business leaders, philanthropists, and community advocates for a program celebrating service, leadership, and humanitarian impact.</p>
<h2>Leadership Training Alongside the Founder</h2>
<p>Arya recently completed the Harvard Medical School Global Healthcare Leaders Program alongside Cassagnol, a credential that underscores the leadership dimension of the award. The program is designed for physicians and healthcare executives working to strengthen health systems and lead organizations through change.</p>
<h2>Two Decades in Advanced Gastroenterology</h2>
<p>Arya is a board-certified gastroenterologist who has served as Director of Advanced Gastroenterology at White Plains Hospital in Westchester County since July 2022. Before that, he was Director of Advanced Endoscopy in the gastroenterology department at NewYork-Presbyterian Brooklyn Methodist Hospital, where he started the only advanced therapeutic endoscopy fellowship program in Brooklyn, according to Becker's ASC.</p>
<p>His clinical focus is the advancement of gastrointestinal endoscopic techniques, with a particular interest in evolving endoscopic approaches for complex pancreaticobiliary disease, luminal tumors, and interventional endosonography.</p>
<p>Arya earned his medical degree from St. George's University School of Medicine in Grenada, completed his internal medicine residency at Long Island Jewish Medical Center, an advanced therapeutic endoscopy fellowship at Lenox Hill Hospital, and a gastroenterology fellowship at Allegheny General Hospital in Pittsburgh. He is a member of the American Society for Gastrointestinal Endoscopy, the American College of Gastroenterology, and the Medical Society of the State of New York.</p>
<h2>Diaspora Connection</h2>
<p>Arya is a prominent figure in the Indian-American medical community &mdash; he founded the New York City metro chapter of the American Association of Physicians of Indian Origin, the largest ethnic medical organization in the United States. The gala's premier sponsorship by the Arya Family Foundation adds a family dimension to the evening's recognition.</p>
<h2>What's Next</h2>
<p>The gala takes place on September 19 in Nyack. For WCFR, now marking its 15th year, the evening doubles as a fundraiser for its global first-responder education programs.</p>''',
})

# ============ 2. Rajeev Ram (sports) ============
ARTICLES.append({
 'topic_id': '487e0559-99a8-40ba-81e3-12ed3dcc182a',
 'llm_score': 4,
 'headline': 'Rajeev Ram Retires After US Open Semifinal Loss, Ending Storied Doubles Career',
 'subheadline': 'The former world No. 1 doubles star played his final match alongside Joe Salisbury on September 11, then gave a tearful on-court farewell honoring his late father.',
 'slug': 'rajeev-ram-retires-us-open-farewell',
 'category': 'sports',
 'vertical': 'sports',
 'article_type': 'breaking',
 'tags': ['Rajeev Ram', 'tennis', 'US Open', 'doubles', 'Joe Salisbury', 'retirement'],
 'sources': [
   'https://www.indystar.com/story/sports/2026/09/12/rajeev-ram-retires-tennis-doubles-play-winning-six-grand-slam-titles-u-s-open-loss/91730904007/',
   'https://ianslive.in/us-open-rajeev-ram-wraps-up-legendary-career-after-mens-doubles-sf-loss--20260911102935',
   'https://www.newkerala.com/news/a/us-open-rajeev-ram-wraps-up-legendary-career-929.htm',
   'https://en.wikipedia.org/wiki/Rajeev_Ram',
 ],
 'diaspora_angle': 'The greatest Indian-American tennis player of all time says goodbye at the tournament where he built his legacy.',
 'image_url': None,
 'image_caption': 'Rajeev Ram at the US Open, where he won three consecutive men\'s doubles titles from 2021 to 2023. The former doubles world No. 1 retired after his final match on September 11, 2026.',
 'image_attribution': '',
 'body': '''<div class="key-takeaways"><ul>
<li>Rajeev Ram, 42, played the final match of his career on September 11, losing the US Open men's doubles semifinal with Joe Salisbury to Kevin Krawietz and Tim Puetz, 6-3, 6-4.</li>
<li>The former doubles world No. 1 retires with six Grand Slam titles, 32 ATP doubles trophies, two Olympic silver medals, and a record 26 consecutive US Open men's doubles appearances.</li>
<li>Ram and Salisbury's three straight US Open titles from 2021 to 2023 remain the only men's doubles three-peat in tournament history.</li>
<li>After the match, Ram gave a tearful on-court tribute to his late father: "I hope I made you proud, Dad."</li>
</ul></div>
<p>Rajeev Ram's storied tennis career ended where so many of its greatest chapters were written. The 42-year-old doubles specialist played his final professional match on Friday, falling with longtime partner Joe Salisbury to Germany's Kevin Krawietz and Tim Puetz 6-3, 6-4 in the US Open men's doubles semifinals.</p>
<p>Ram, a former world No. 1 in doubles, announced his retirement immediately afterward, closing a career that produced six Grand Slam titles, 32 ATP doubles championships, and two Olympic silver medals.</p>
<h2>A Farewell at Flushing Meadows</h2>
<p>The semifinal was a fitting stage. Ram and Salisbury won the US Open together in 2021, 2022, and 2023 &mdash; the only men's doubles three-peat in the tournament's history &mdash; and Ram's 26 consecutive appearances in the US Open men's doubles draw are the most ever recorded, according to IANS.</p>
<blockquote class="pull-quote">
<p>"Honestly, it couldn't have been better. The whole thing, to me, couldn't have been any better. My family was there. My wife and my mom were there. My college coach was there. My former partner Eric Butorac was there, and now he is the tournament director. My longstanding partner Joe Salisbury, with whom I've shared so many good memories, was there as well."</p>
<cite>&mdash; Rajeev Ram, to USOpen.org after his final match</cite>
</blockquote>
<p>USTA chief executive Craig Tiley &mdash; Ram's college coach at the University of Illinois &mdash; and US Open tournament director Eric Butorac, Ram's former doubles partner, joined the on-court ceremony honoring his career.</p>
<h2>A Tearful Tribute to His Father</h2>
<p>The most emotional moment came when Ram remembered his father, Raghav Ram, who introduced him to the sport and died in 2019.</p>
<blockquote class="pull-quote">
<p>"There's one special person who's not here today, and that's my dad. He taught me how to play this game, and he gave me a chance to play on these wonderful courts like this. So, I hope I made you proud, Dad."</p>
<cite>&mdash; Rajeev Ram, at his US Open farewell ceremony</cite>
</blockquote>
<h2>From Denver to Doubles Dominance</h2>
<p>Born in Denver on March 18, 1984, and raised in Carmel, Indiana, Ram won an Indiana state singles championship before playing college tennis at the University of Illinois. He turned professional in 2004 and initially focused on singles, reaching No. 56 in the world and winning two tour titles, both in Newport.</p>
<p>His pivot to doubles unlocked one of the great careers of the modern era. Beyond the US Open three-peat, Ram won the 2020 Australian Open men's doubles title, the ATP Finals in 2022 and 2023, and six Masters 1000 events. His two mixed-doubles Grand Slam titles came at the Australian Open in 2019 and 2021, both with Barbora Krejcikova. He won Olympic silver in mixed doubles with Venus Williams at Rio 2016 and in men's doubles with Austin Krajicek at Paris 2024, and he was a longstanding contributor to the U.S. Davis Cup team. His career prize money stands at $10.36 million, according to ATP records.</p>
<h2>Diaspora Pride</h2>
<p>Diaspora outlets have embraced Ram as one of their own &mdash; The American Bazaar described him as the greatest Indian American tennis player of all time. For a generation of young Indian-American players who grew up watching an Indian name lift Grand Slam trophies in New York, his career has been both a benchmark and a blueprint.</p>
<h2>What's Next</h2>
<p>Ram has not announced his post-playing plans. If his on-court farewell is any guide &mdash; surrounded by family, coaches, and partners &mdash; the next chapter is likely to keep him close to the sport that defined his adult life.</p>''',
})

for a in ARTICLES:
    a['word_count'] = wc(a['body'])
    fn = os.path.join(STATE, 'v3-article-%s.json' % a['topic_id'])
    with open(fn, 'w') as f:
        json.dump(a, f, indent=1, ensure_ascii=False)
    print('%s | slug=%s | words=%d' % (a['topic_id'], a['slug'], a['word_count']))
