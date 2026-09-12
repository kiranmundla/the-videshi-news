#!/usr/bin/env python3
"""Second trim pass. Exact-string replacements."""
import json, os, re, subprocess

SUPABASE_URL = os.environ["SUPABASE_URL"]
KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

def curl(method, path, data=None, params=""):
    cmd = ["curl", "-sS", "-X", method,
           f"{SUPABASE_URL}/rest/v1/{path}{params}",
           "-H", f"apikey: {KEY}",
           "-H", f"Authorization: Bearer {KEY}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=representation"]
    if data is not None:
        cmd += ["-d", json.dumps(data)]
    out = subprocess.run(cmd, capture_output=True, text=True, check=True)
    return out.stdout

def get_body(aid):
    return json.loads(curl("GET", "p2_articles", params=f"?select=body&id=eq.{aid}"))[0]["body"]

def set_body(aid, body):
    text = re.sub(r"<[^>]+>", " ", body)
    n = len([w for w in text.split() if w.strip()])
    curl("PATCH", "p2_articles", data={"body": body, "word_count": n}, params=f"?id=eq.{aid}")
    return n

def sub(aid, old, new):
    body = get_body(aid)
    assert old in body, f"NOT FOUND in {aid}: {old[:60]}"
    return set_body(aid, body.replace(old, new, 1))

AID1 = "d774eb31-2f18-4f2c-a8e8-b0f8a7b74ca6"
AID2 = "db228cef-691e-48d9-8d63-cc660d4d164f"
AID3 = "4a64973b-0368-44f3-9429-6b40c35004da"

# --- Article 1 ---
sub(AID1, "Her outspoken assessments span the Khans' three-decade dominance and the industry's shifting audience tastes.",
    "Her assessments span the Khans' three-decade dominance and shifting audience tastes.")
sub(AID1, "In a run of candid interviews — from trade conversations to a recent sit-down that has reignited debate about where Hindi cinema stands — the actor has laid out an unusually blunt account of Bollywood's evolution: the three-decade reign of the Khans, the arrival of streaming as a creative equaliser and an industry being forced to rethink its storytelling.",
    "In a run of candid interviews — including a recent sit-down that reignited debate about Hindi cinema — the actor has laid out an unusually blunt account of Bollywood's evolution: the three-decade reign of the Khans, streaming as a creative equaliser and an industry rethinking its storytelling.")
sub(AID1, "Bhasker entered Hindi cinema in 2009 and broke through with <em>Tanu Weds Manu</em> (2011), <em>Raanjhanaa</em> (2013) and <em>Nil Battey Sannata</em> (2016), straddling big commercial titles such as <em>Prem Ratan Dhan Payo</em> (2015) and <em>Veere Di Wedding</em> (2018), and independent cinema.",
    "Bhasker broke through with <em>Tanu Weds Manu</em> (2011), <em>Raanjhanaa</em> (2013) and <em>Nil Battey Sannata</em> (2016), straddling commercial titles like <em>Prem Ratan Dhan Payo</em> (2015) and <em>Veere Di Wedding</em> (2018), and independent cinema.")
sub(AID1, 'She cautioned that the old order had not finished adapting: "It is yet to be seen how the traditional box office determined ecosystem of theatrical cinema will readjust to this change." Six years on, that readjustment is still underway, with 2026 box-office data showing theatrical revenues increasingly concentrated in a handful of tentpoles.',
    'Six years on, that readjustment is still underway, with 2026 box-office data showing theatrical revenues increasingly concentrated in a handful of tentpoles.')
sub(AID1, '"After the unfortunate and tragic suicide of Sushant, Bollywood has been painted as a really dark place, that is only about drugs and alcohol and sex," she said.',
    '"After the unfortunate and tragic suicide of Sushant, Bollywood has been painted as a really dark place," she said.')
sub(AID1, "In a 2025 conversation with Hauterrfly, she revisited the controversy over <em>Raanjhanaa</em> (2013), criticised for glorifying stalking, admitting she had not recognised the problem while making it.",
    "In a 2025 conversation with Hauterrfly, she revisited the controversy over <em>Raanjhanaa</em> (2013) — criticised for glorifying stalking — admitting she had not seen the problem while making it.")
sub(AID1, '"An actor can become a star, but to retain that position like SRK, Salman or Aamir for 25 years is difficult," she said at a 2017 industry event. Nine years later, trade analysts say Hindi cinema still has not built a successor generation to replace them.',
    '"An actor can become a star, but to retain that position like SRK, Salman or Aamir for 25 years is difficult," she said in 2017 — and trade analysts say Hindi cinema still has not built a successor generation.')
sub(AID1, "Bhasker attributes Bollywood's box-office slump to an economic slowdown, COVID-19 and the rise of OTT — not only to boycott campaigns.",
    "Bhasker blames Bollywood's box-office slump on the economic slowdown, COVID-19 and OTT — not just boycott campaigns.")

# --- Article 2 ---
sub(AID2, "Hollywood's share hit a record 17%, beating its 2019 peak of 15%; <em>Spider-Man: Brand New Day</em> crossed ₹500 crore to become the highest-grossing international film ever in India.",
    "Hollywood's share hit a record 17%; <em>Spider-Man: Brand New Day</em> crossed ₹500 crore, the highest-grossing international film ever in India.")
sub(AID2, "Coupled with Christopher Nolan's <em>The Odyssey</em> (₹220 crore), international films generated over ₹1,424 crore between January and July — putting Hollywood on track to eclipse its pre-pandemic 2019 revenue record of ₹1,595 crore well before the year-end release of <em>Avengers: Doomsday</em>.",
    "Alongside Christopher Nolan's <em>The Odyssey</em> (₹220 crore), international films generated over ₹1,424 crore through July — on track to eclipse Hollywood's 2019 India revenue record of ₹1,595 crore.")
sub(AID2, "The primary disruptor in 2026 has been international cinema, which expanded its domestic footprint to a record-high 17% share of total Indian box-office revenue through July. Hollywood's previous annual best stood at 15% in 2019.",
    "International cinema was the primary disruptor in 2026, expanding to a record-high 17% share of domestic box-office revenue through July — Hollywood's previous annual best was 15% in 2019.")
sub(AID2, "For the first time in 2026, Hindi cinema's share of the domestic box office has slipped below 40%, settling at 38% through July — down sharply from the 44% it commanded at the end of June.",
    "For the first time in 2026, Hindi cinema's share has slipped below 40%, settling at 38% through July — down from 44% at the end of June.")
sub(AID2, "The squeeze has two engines. Hollywood franchises open day-and-date with massive dubbed footprints and premium-format pricing, pulling the top end of the audience. Regional cinema is eating the middle: it recovered faster from the pandemic, takes bigger creative risks and now releases pan-India with Hindi dubs as a matter of course.",
    "Hollywood franchises now open day-and-date with massive dubbed footprints, pulling the top end of the audience, while regional cinema — which recovered faster from the pandemic — eats the middle with pan-India dubbed releases.")
sub(AID2, "For Bollywood, the danger is not a bad year — 2026 is, in aggregate, a record one — but a shrinking claim on it. When a single Hollywood title can outgross every Hindi release of the month except the year's biggest, the centre of gravity has moved.",
    "For Bollywood, the danger is not a bad year — 2026 is a record one — but a shrinking claim on it. When a single Hollywood title outgrosses every Hindi release of the month except the year's biggest, the centre of gravity has moved.")

# --- Article 3 ---
sub(AID3, "Rediff critic Sukanya Verma spotlights Hindi cinema's new wave of women in uniform, from Kareena Kapoor Khan's \"cop who wears lipstick\" in <em>Daayra</em> to Rani Mukerji's Shivani Shivaji Roy in the <em>Mardaani</em> films.",
    "Rediff's Sukanya Verma spotlights Hindi cinema's new wave of women in uniform, from Kareena Kapoor Khan's \"cop who wears lipstick\" in <em>Daayra</em> to Rani Mukerji's Shivani Shivaji Roy.")
sub(AID3, "According to Bollywood Hungama, it made the <em>Mardaani</em> series the only female-cop franchise to succeed in 113 years of Hindi cinema, landing an unprecedented hattrick of hits.",
    "It made the <em>Mardaani</em> series the only female-cop franchise to succeed in 113 years of Hindi cinema.")
sub(AID3, "Hema Malini wore the khaki in <em>Andhaa Kaanoon</em> (1983). Rekha headlined <em>Phool Bane Angaray</em> (1991), playing an officer transformed from grieving widow into seeker of justice.",
    "Hema Malini wore the khaki in <em>Andhaa Kaanoon</em> (1983); Rekha headlined <em>Phool Bane Angaray</em> (1991).")
sub(AID3, '"What ends up happening," says <em>Brown</em> director Abhinay Deo, "is that even if a woman-centric film does well, there is no comparison to a man-centric film doing well. We\'re talking about ticket sales and the film scenario, until OTT came along."',
    '"Even if a woman-centric film does well, there is no comparison to a man-centric film doing well," says <em>Brown</em> director Abhinay Deo. "We\'re talking about ticket sales and the film scenario, until OTT came along."')
sub(AID3, "Raveena Tandon's Kasturi Dogra navigated a murder mystery in <em>Aranyak</em> while juggling family pressures and workplace scepticism. Bhumi Pednekkar's Rita Ferreira in <em>Daldal</em> brought a morally conflicted protagonist to the screen; Mona Singh's Baljit Kaur gave Punjabi crime drama its most textured female lead in <em>Kohrra</em>; Kareena Kapoor Khan's Jasmeet Kaur Bedi carried a cold-case investigation in England in <em>The Buckingham Murders</em>; Deepika Padukone entered Rohit Shetty's cop universe as Shakti Shetty in <em>Singham Again</em>. In June 2026, Karisma Kapoor returned in <em>Brown</em> as Rita Brown, a recovering alcoholic detective with the Kolkata police — flawed, unglamorous, fiercely complex.",
    "Raveena Tandon's Kasturi Dogra juggled a murder mystery with family pressures in <em>Aranyak</em>; Bhumi Pednekkar's Rita Ferreira was the flawed heart of <em>Daldal</em>; Mona Singh's Baljit Kaur anchored <em>Kohrra</em>; Kareena Kapoor Khan carried a cold case in England in <em>The Buckingham Murders</em>; Deepika Padukone entered Rohit Shetty's cop universe in <em>Singham Again</em>. In June 2026, Karisma Kapoor returned in <em>Brown</em> as Rita Brown, a recovering alcoholic detective with the Kolkata police.")
sub(AID3, '<p>Rasika Dugal, who plays ACP Neeti Singh in <em>Delhi Crime</em>, extends the point: "There can be a lot of power with a soft exterior as well." Her character is petite, softly spoken and consistently underestimated — a deliberate rejection of the idea that women in control must behave in a masculine fashion.</p>\n',
    '')
sub(AID3, "The creative change had to survive the commercial one, and <em>Mardaani 3</em> is the strongest evidence it did. When the first film released in 2014, Mukerji's Shivani Roy was a rarity — a mainstream Hindi action heroine, neither young nor glamorous, carrying the film's moral and commercial weight alone. The franchise survived a six-year gap between instalments and returned in 2026 to its best numbers yet. The remaining fault line runs between platforms: digital has embraced female-first narratives, while theatrical box-office pressure still decides whether the industry's faith holds.",
    "The creative change had to survive the commercial one, and <em>Mardaani 3</em> is the strongest evidence it did: when the first film released in 2014, Mukerji's Shivani Roy — a mainstream Hindi action heroine, neither young nor glamorous — carried the film's weight alone. The franchise survived a six-year gap and returned in 2026 to its best numbers yet.")
sub(AID3, '"Even today, when I wear that uniform, I get goosebumps," Shah says. "Every single time I wear it, I stand differently."',
    '')
sub(AID3, '"Portraying authority on screen isn\'t about volume or aggression. It\'s about stillness, conviction and knowing exactly when to push and when to hold back," Sinha says of Anjali Bhaati. "Perfection is no longer interesting. With Anjali, her flaws and vulnerabilities don\'t take away from her strength, they define it."',
    '"Portraying authority on screen isn\'t about volume or aggression. It\'s about stillness, conviction and knowing exactly when to push and when to hold back," Sinha says. "With Anjali, her flaws and vulnerabilities don\'t take away from her strength, they define it."')
sub(AID3, "Rohit Shetty has confirmed a standalone film for Deepika Padukone's Lady Singham, and Kareena Kapoor Khan's <em>Daayra</em> will test whether the theatrical audience for women-led crime stories keeps growing.",
    "Rohit Shetty has confirmed a standalone film for Deepika Padukone's Lady Singham, and Kareena Kapoor Khan's <em>Daayra</em> will test whether the theatrical audience keeps growing.")

# final counts
for aid in (AID1, AID2, AID3):
    body = get_body(aid)
    text = re.sub(r"<[^>]+>", " ", body)
    print(aid, len([w for w in text.split() if w.strip()]))
