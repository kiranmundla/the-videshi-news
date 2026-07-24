#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-23 23:00 PDT
Key updates this cycle:
- MAJOR: Trump says Iran deal 'largely negotiated', Strait of Hormuz will be opened
- Axios: 60-day ceasefire extension proposed — Hormuz reopens, Iran sells oil freely, nuclear talks begin
- Pakistan Army Chief Asim Munir in Tehran mediating; Iran signals 'narrowing differences'
- Rubio met Modi in Delhi, extended White House invite; Jaishankar bilateral Sunday
- Rubio told journalists in India 'there's been some progress' on Iran
- Cannes 2026 Palme d'Or: Cristian Mungiu's 'Fjord' (Sebastian Stan) — Neon's 7th consecutive win
- Nepal's 'Elephants In The Fog' makes Cannes history; Virginie Efira wins Best Actress
- IPL unchanged: PBKS beat LSG (Shreyas Iyer 101*); tomorrow MI vs RR + KKR vs DC decides 4th spot
- Kohli-Head handshake snub continues to dominate cricket headlines globally
"""

import json
import os
from datetime import datetime, timezone

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TECH_BUZZ = os.path.join(SCRIPT_DIR, "..", "public", "data", "tech-buzz.json")
CELEB_BUZZ = os.path.join(SCRIPT_DIR, "..", "public", "data", "celebrity-buzz.json")


def update_tech_buzz():
    with open(TECH_BUZZ) as f:
        data = json.load(f)

    leaders_by_handle = {l["handle"]: l for l in data.get("leaders", [])}
    updated = 0

    updates = {
        # === TECH PULSE ===
        "elonmusk": {
            "text": "SpaceX IPO filing targets $1.75 trillion valuation per JPMorgan — S&P 500 inclusion could force $950B in passive fund reallocation. Starship completes 12th test flight. Meanwhile Trump says Iran deal 'largely negotiated' — Hormuz reopening would ease global oil markets and boost tech sentiment.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-23",
        },
        "zuck": {
            "text": "Meta confirms 15,000 total job actions — 8,000 cut, 7,000 reassigned to AI teams. Spending $115-135B on AI infrastructure in 2026. Leaked audio: Zuckerberg defended employee surveillance to win the AI race. Threads crosses 150M daily users. Cannes 2026 wraps — Mungiu's 'Fjord' wins Palme d'Or.",
            "url": "https://x.com/zuck",
            "date": "2026-05-23",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI across Search, Workspace, and Cloud. Antitrust concerns mount. Quad FM meeting in New Delhi on May 26 — Rubio already met Modi, bilateral with Jaishankar on Sunday. Google's India investments under spotlight as Big Tech pours $50B into India.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-23",
        },
        "satyanadella": {
            "text": "Microsoft defends $80B AI infrastructure investment as Azure crosses $75B quarterly revenue. Copilot enterprise adoption at record highs. Iran deal breakthrough — if Hormuz reopens and oil markets stabilize, tech spending momentum strengthens further.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-23",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 — 'smarter than the smartest person' — as Musk v. OpenAI lawsuit heads toward trial. OpenAI's valuation soars. Bill Gates argues AI development pauses are counterproductive. The AGI race enters its most intense phase.",
            "url": "https://x.com/sama",
            "date": "2026-05-23",
        },
        "tim_cook": {
            "text": "Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator.' Apple asks Supreme Court to review App Store contempt ruling. WWDC 2026 AI features incoming. Cannes wraps — Hollywood largely absent as tech firms dominate global attention.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-23",
        },
        "nvidia": {
            "text": "Nvidia posts jaw-dropping $81.6B Q1 revenue — 10x from three years ago. Vera Rubin platform: 10x inference throughput per megawatt over Blackwell. CEO Huang sees $1 trillion in orders but concedes China market to Huawei. Dow near record ~50,563 as Iran deal breakthrough lifts markets.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-23",
        },
        "NandanNilekani": {
            "text": "Big Tech pours $50B into India for AI, cloud, and digital infrastructure. Rubio's India visit — first US diplomatic trip to Kolkata in 14 years — highlights India as key tech partner. Quad FM meeting May 26 will discuss critical tech. India emerges as top AI talent hub.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-23",
        },
        "BillGates": {
            "text": "Bill Gates criticizes AI development pauses — argues stopping progress risks ceding ground to less safety-conscious actors. Kevin Warsh, whom Gates has advised, takes the Fed chair. Iran deal 'largely negotiated' — Warsh's first test may be navigating oil market volatility.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-23",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise Generative AI adoption using watsonx platform. India emerging as major enterprise AI deployment hub as $50B Big Tech investment wave lands.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-23",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO continues integrating generative AI across Creative Cloud and Experience Cloud. Firefly models gain traction against Midjourney and DALL-E. Cannes 2026 closes — 'Fjord' wins Palme d'Or as AI-generated content debate intensifies in film industry.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-23",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal maintains low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley. The Indian-American tech diaspora continues shaping global AI leadership.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair steers the luxury house through a competitive landscape. Cannes 2026 wraps — Aishwarya Rai dazzled in couture, Aaradhya's red carpet debut, and Mungiu's 'Fjord' takes the Palme d'Or. Indian-born diaspora influence in luxury leadership grows.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-23",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates global logistics amid trade disruptions. Trump says Iran deal 'largely negotiated' — Strait of Hormuz reopening would be transformative for global shipping routes. Indian-American CEO at the helm of a Fortune 50 logistics giant.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-23",
        },

        # === INDIA PULSE ===
        "narendramodi": {
            "text": "PM Modi hosts US Secretary of State Rubio — wide-ranging talks on trade, defense, energy, Indo-Pacific. Trump invites Modi to White House via Rubio. US calls India 'vital partner.' Jaishankar-Rubio bilateral on Sunday ahead of Quad FM Meeting May 26. Rubio visited Kolkata — first US envoy in 14 years.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-23",
        },
        "PMOIndia": {
            "text": "India-US ties deepen as Rubio's 4-day visit (Kolkata → Delhi → Agra → Jaipur) sets stage for Quad FM meeting May 26. 'Mission 500' to double trade by 2030 discussed. Rubio tells journalists in India: 'there's been some progress' on Iran. India positioned as key player in Iran peace framework.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-23",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah oversees national security preparations as Rubio visits India ahead of Quad FM meeting. Counter-terrorism, defense cooperation remain key bilateral items. Trump says Iran deal 'largely negotiated' — India's energy security implications enormous.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-23",
        },
        "RahulGandhi": {
            "text": "Congress leader Rahul Gandhi renews attacks on Modi-Adani ties as Adani Group expands into power, telecom, and green energy. Opposition sharpens criticism amid $50B Big Tech investment wave and $22.2B FPI outflow concerns. Rubio's White House invite to Modi draws attention.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-23",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath continues aggressive infrastructure push in India's most populous state. Rubio's Kolkata visit — first by a US envoy in 14 years — signals expanding diplomatic footprint beyond Delhi. UP positions itself for Big Tech's $50B India investment wave.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-23",
        },
        "ArvindKejriwal": {
            "text": "AAP leader Kejriwal steps up opposition rhetoric. Delhi politics intensifies as Rubio meets Modi, Iran deal reaches 'largely negotiated' status, $22.2B FPI outflows concern markets, and Quad FM meeting approaches Monday.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-23",
        },
        "DrSJaishankar": {
            "text": "EAM Jaishankar to hold bilateral with Rubio on SUNDAY ahead of Quad FM Meeting May 26. Rubio already met Modi today — 'Trade, Technology, Defense, QUAD' on agenda per US ambassador. Rubio: 'some progress' on Iran. India's diplomatic moment — four-nation engagement in Delhi this week.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-23",
        },
        "nsitharaman": {
            "text": "Finance Minister Sitharaman monitors India's economic outlook — $50B Big Tech investments land while FPI outflows hit $22.2B and rupee near ₹94. Iran deal breakthrough could ease oil import costs significantly. Kevin Warsh's Fed debut adds rate uncertainty.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-23",
        },
        "rashtrapatibhvn": {
            "text": "President Droupadi Murmu presides as India hosts critical Quad diplomacy. Four nations — US, India, Japan, Australia — converge on Delhi for May 26 FM meeting. India's global standing strengthens as Trump calls Iran deal 'largely negotiated.'",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-23",
        },
        "gautam_adani": {
            "text": "Adani Group pushes into green energy, ports, data centers as India attracts $50B Big Tech wave. Reliance-Adani rivalry intensifies after Ambani scraps family noncompete. Faces renewed attacks from Rahul Gandhi. Iran deal could reshape India's energy import landscape.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-23",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands into power and telecom after scrapping family noncompete. $1B telecom infrastructure investment, clean energy push, shares up 4.9%. Iran deal breakthrough — if Hormuz reopens and sanctions ease, India's energy costs could drop sharply.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-23",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its legacy of philanthropy and nation-building. Tata Group companies remain at forefront as India attracts record foreign investment. Cannes 2026 wraps — India's cultural soft power on display alongside its economic rise.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-23",
        },

        # === WORLD / POWER PULSE ===
        "realDonaldTrump": {
            "text": "BREAKING: Trump says Iran deal 'LARGELY NEGOTIATED' — Strait of Hormuz will be opened. Axios: 60-day ceasefire extension proposed — Hormuz reopens with no tolls, Iran sells oil freely, nuclear enrichment talks begin. Pakistan's Gen Asim Munir in Tehran mediating. Still meeting advisers tonight.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-23",
        },
        "WhiteHouse": {
            "text": "Iran deal upgraded to 'largely negotiated' — 60-day ceasefire extension: Hormuz reopens, Iran clears mines, US lifts port blockade, sanctions waivers for oil sales, Iran commits to never pursue nuclear weapons + negotiate enrichment suspension. Gabbard exits DNI June 30; Aaron Lukas acting. Warsh at Fed.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-23",
        },
        "Keir_Starmer": {
            "text": "UK PM Starmer co-chaired 40+ nation Paris meeting with Macron on Strait of Hormuz security. Trump now says deal 'largely negotiated' — Hormuz reopening would ease UK energy costs significantly. Free summer bus travel for kids announced. Reform UK's Farage circles.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-23",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosted 40+ nation Paris summit on Hormuz security. Hours later, Trump says Iran deal 'largely negotiated' and Hormuz will open. 60-day ceasefire extension proposed. France at center of peace effort. Oil at $106.92 — could drop sharply if deal holds.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-23",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad FM meeting in New Delhi May 26. Trump's Iran deal breakthrough adds urgency — Hormuz reopening affects Indo-Pacific energy security. Australia's FM to meet Modi alongside Jaishankar and Rubio.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-23",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni's viral 'Melody' candy moment with Modi strengthens Italy-India ties. Trump says Iran deal 'largely negotiated' tonight — Hormuz reopening would ease European energy costs. G7 coordination on Iran response intensifies.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-23",
        },
        "HHShkMohd": {
            "text": "UAE ruler MBR watches Iran deal breakthrough closely — Trump says 'largely negotiated,' Hormuz will open. 60-day ceasefire extension with no tolls and mine clearance proposed. Gulf nations push for permanent resolution. Oil markets brace for potential price correction.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-23",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Luxon monitors Indo-Pacific developments as Quad FM meeting approaches. Iran deal now 'largely negotiated' — Five Eyes alignment and Pacific security priorities shift as Hormuz crisis nears resolution.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-23",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy continues post-DOGE political trajectory. Gabbard's resignation as DNI (husband's cancer) makes him the highest-profile Indian-American to have served and departed Trump's inner circle. His Ohio political ambitions and 'anti-woke' brand remain active.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-23",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak observes from opposition as Starmer navigates Iran deal breakthrough and Reform UK's rise. Sunak's legacy as Britain's first Indian-origin PM continues to resonate with the global diaspora.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-23",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance — Indian-American Yale Law grad — watches as VP JD Vance returns to DC for Iran deal deliberations. Trump says deal 'largely negotiated' tonight — the entire national security team working through the weekend.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-23",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel continues reshaping the Bureau. Gabbard's resignation as DNI — departing June 30 — leaves Aaron Lukas as acting director. Indian-American influence in national security remains strong. Iran deal 'largely negotiated' keeps intelligence community at full throttle.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-23",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan shapes US tech policy as Big Tech pours $50B into India and SpaceX files for a $1.75T IPO. Rubio in India meeting Modi — tech cooperation central to Quad agenda. Iran deal breakthrough could stabilize global markets for tech investment.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-23",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman — Indian-origin Tory — remains vocal on immigration from backbenches as Starmer faces Reform UK pressure and navigates Iran deal fallout.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-22",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga shapes global development policy as India hosts Quad FM meeting and Iran deal reaches 'largely negotiated' status. Hormuz reopening would transform global trade flows — World Bank monitors oil market impact on developing nations.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-23",
        },

        # === SPORTS PULSE ===
        "imVkohli": {
            "text": "CONTROVERSY: Kohli refuses handshake with Travis Head after SRH's 55-run win — video goes viral globally. Kohli gestured for Head to 'come bowl,' scored 15 before falling. RCB finish TOP with 18 pts (best NRR). Qualifier 1 vs Gujarat Titans on May 27 at Dharamsala.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-23",
        },
        "ImRo45": {
            "text": "Mumbai Indians (4-9, eliminated) face Rajasthan Royals at Wankhede TOMORROW in IPL's biggest spoiler match. If MI beat RR, Punjab Kings (15 pts) take the 4th playoff spot. Rohit's dead rubber decides three teams' fates. The final day's results reshape everything.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-23",
        },
        "msdhoni": {
            "text": "CSK eliminated from IPL 2026. Captain Cool watches as PBKS kept playoff hopes alive — Shreyas Iyer's stunning 101* (off ~55 balls). Tomorrow's double-header at Wankhede and Eden Gardens decides the 4th spot. The next generation plays on.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-23",
        },
        "Jaspritbumrah93": {
            "text": "Bumrah left out of India's T20 World Cup squad — managed carefully for longer formats. MI face RR tomorrow at Wankhede in the most consequential dead rubber in IPL history. MI's result decides the 4th playoff spot for three other teams.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-23",
        },
        "hardikpandya7": {
            "text": "MI face Rajasthan Royals at Wankhede TOMORROW — MI's dead rubber is RR's knockout. If RR lose, PBKS (15 pts) take the 4th spot. Hardik's MI can play kingmaker on IPL's most dramatic final day. Three teams' fates hang on two results.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-23",
        },
        "BCCI": {
            "text": "IPL 2026 FINAL DAY TOMORROW: MI vs RR (Wankhede) + KKR vs DC (Eden Gardens). Top 3 locked: RCB (1st, 18 pts), GT (2nd, 18), SRH (3rd, 18). PBKS (15 pts, done) pray for RR AND KKR losses. RR (14 pts) just need a win. KKR (13 pts) need to win + RR loss. Drama guaranteed.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-23",
        },
        "ICC": {
            "text": "ICC board meeting in Ahmedabad May 30 to discuss playing conditions. Kohli-Head handshake controversy dominates global cricket headlines. T20 World Cup squad selections create ripples. Cannes wraps; IPL final day tomorrow. Two massive global events in one weekend.",
            "url": "https://x.com/ICC",
            "date": "2026-05-23",
        },
        "IPL": {
            "text": "TONIGHT: PBKS 200/3 beat LSG 196/6 by 7 wickets — Shreyas Iyer smashes maiden IPL century (101*). PBKS at 15 pts. TOMORROW decides it all: Match 69 MI vs RR (Wankhede), Match 70 KKR vs DC (Eden Gardens). Three teams, one spot. Playoffs start May 27.",
            "url": "https://x.com/IPL",
            "date": "2026-05-23",
        },
        "Neeraj_chopra1": {
            "text": "India's golden arm Neeraj Chopra preps for the 2026 athletics season. Federation Cup in Ranchi spotlights India's next wave of track and field talent. Diamond League circuit awaits the Olympic champion's return.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-23",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu continues her badminton campaign as the international circuit heats up. India's shuttlers build momentum through Super Series events ahead of the Asian Games cycle.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Tennis icon Sania Mirza's legacy continues to inspire Indian tennis. Post-retirement, she remains the most prominent Indian face in global tennis, mentoring the next generation.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh takes a classical break to prepare for title defense against Candidates winner Sindarov. GM Nepomniachtchi: 'Every top GM would have a good chance against him.' The youngest world champion plots his comeback.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-23",
        },
        "chetrisunil11": {
            "text": "AIFF announces 2026-27 Club Licensing results as Indian football restructures. Sunil Chhetri's legacy as India's all-time top scorer endures — the next generation looks to carry the torch he lit.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-23",
        },
        "sachin_rt": {
            "text": "The Master Blaster watched son Arjun play for LSG in IPL 2026. PBKS chased down LSG's 196/6 tonight — Shreyas Iyer's 101* sealed a 7-wicket win. Tomorrow's double-header decides the 4th playoff spot. Cricket's greatest legacy extends to the next generation.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-23",
        },
        "SGanguly99": {
            "text": "Former BCCI president Saurav Ganguly watches IPL 2026's thrilling final weekend. KKR — the franchise he built — face DC at Eden Gardens TOMORROW in do-or-die for the 4th spot. Need to win AND hope RR lose. The Dada legacy looms large.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-23",
        },
    }

    for handle, update in updates.items():
        if handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            if "latestPost" in leader:
                leader["latestPost"]["text"] = update["text"]
                leader["latestPost"]["url"] = update["url"]
                leader["latestPost"]["date"] = update["date"]
            elif "text" in leader:
                leader["text"] = update["text"]
                leader["url"] = update["url"]
                leader["date"] = update["date"]
            updated += 1
        else:
            print(f"⚠️  Handle '{handle}' not found in tech-buzz.json")

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(TECH_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ tech-buzz.json: {updated}/{len(updates)} leaders updated")


def update_celebrity_buzz():
    celeb_posts = [
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "BREAKING: Trump says Iran deal 'LARGELY NEGOTIATED' — Strait of Hormuz will open. Axios: 60-day ceasefire extension with no-toll Hormuz passage, Iran clears mines, US lifts port blockade, sanctions waivers for oil. Iran commits to never pursue nukes. Pakistan's Gen Asim Munir mediating in Tehran.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "HANDSHAKE GATE: Kohli refuses Travis Head's handshake — video goes viral globally. Head's cryptic Instagram story adds fuel. RCB finish TOP with 18 pts. Qualifier 1 vs GT on May 27 at Dharamsala. Tomorrow's double-header decides the 4th playoff spot — three teams, one seat.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi hosts Rubio — Trump invites Modi to White House. US calls India 'vital partner.' Rubio's 4-city trip (Kolkata → Delhi → Agra → Jaipur) first US envoy to Kolkata in 14 years. Jaishankar-Rubio bilateral Sunday. 'Mission 500' to double trade by 2030. Iran deal 'largely negotiated.'",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MAIDEN IPL CENTURY! Shreyas Iyer smashes 101* as PBKS chase down LSG's 196/6 with 7 wickets in hand. Punjab climb to 15 pts. Now need MI to beat RR AND KKR to lose to DC tomorrow. The most dramatic IPL final day in years — three teams, one spot.",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborofficial",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Aishwarya dazzles at Cannes 2026 closing day in Amit Aggarwal couture. Daughter Aaradhya's red carpet debut in ruby-red steals hearts. Cannes wraps: 'Fjord' (Sebastian Stan) wins Palme d'Or. Nepal's 'Elephants In The Fog' makes history. L'Oréal Gala celebrates women in cinema.",
            "url": "https://www.instagram.com/aaborofficial/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX IPO targets $1.75T — potentially the LARGEST ever. S&P 500 inclusion could trigger $950B passive fund reallocation. Starship 12th test flight. Iran deal 'largely negotiated' — if Hormuz reopens, oil drops, and tech sentiment soars. Dow near record ~50,563.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 15,000 total job actions (8K cut + 7K reassigned). $115-135B on AI infra in 2026. Leaked audio: Zuck defends surveillance for AI race. Employees 'miserable' per NYT. Threads hits 150M daily users. Cannes 2026 wraps — culture moves fast.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' — SRK's ₹350 crore action thriller with Suhana and Deepika — may split into two parts. Part 1 eyed for September 2026 (Christmas release Dec 24). Meanwhile KKR face DC at Eden Gardens tomorrow — SRK's team needs a miracle. Dhurandhar hits ₹1,307 crore.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "CSK eliminated from IPL 2026. Captain Cool watches as Shreyas Iyer hits 101* for PBKS. Tomorrow's double-header decides the 4th spot — three teams, one seat. The IPL Dhoni helped build has never been more dramatic on its final league day.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI face RR at Wankhede TOMORROW — MI's dead rubber is RR's knockout. If MI win, PBKS get the 4th spot. Hardik's MI can play kingmaker. Three teams' fates in MI's hands on the most dramatic final day in IPL history.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika uses body double for action in SRK's 'King' and Atlee's 'Raka' due to pregnancy — climactic sequence filming in South Africa. Back from birthday trip in New York with Ranveer. Cannes 2026 wraps: 'Fjord' wins Palme d'Or, Aishwarya and Aaradhya steal red carpet.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit's concert tour continues selling out across North America. The Punjabi superstar is THE face of Indian music going global — bridging Bollywood and the diaspora one sold-out arena at a time. 6 featured events on The Videshi across major US cities.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer's post-apocalyptic thriller 'Pralay' begins filming August 2026 — ₹300 crore budget. Dhurandhar hits ₹1,307 crore heading to Japan. Back from Deepika's birthday trip in New York. Vicky Kaushal blocks 18 months for 'Mahavatar.' Bollywood bets big on 2026-27.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Son Arjun played for LSG — PBKS chased down 196/6 with Shreyas Iyer's 101*. Arjun Tendulkar bowled a yorker dismissal that made highlights. Tomorrow's final day: MI vs RR + KKR vs DC. Three teams, one spot. Cricket's greatest legacy extends to the next generation.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat — GM Nepomniachtchi: 'Every top GM would have a good chance against him.' Gukesh preps for title defense against Sindarov. The youngest world champion plots his comeback amid growing pressure from the old guard.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment, shares up 4.9%. Iran deal 'largely negotiated' — if Hormuz reopens, India's energy costs could drop dramatically. The Ambani-Adani duopoly reshapes India Inc.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra's dual Hollywood-Bollywood career continues. 'Jee Le Zaraa' with Katrina and Alia remains most anticipated. Cannes 2026 wraps: 'Fjord' wins Palme d'Or, Aishwarya and Aaradhya steal the red carpet. Indian star power going global.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's live album generates buzz as her US tour hits 5 cities. The voice of a generation sells out diaspora venues — bringing Bollywood's golden age of playback singing to NRI audiences worldwide.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress (90M+) shares mountain retreat moments between projects. Cannes 2026 wraps with 'Fjord' winning Palme d'Or — Bollywood glamour and global cinema collide as the festival season ends.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia's 2026 slate packed — 'Jee Le Zaraa' with Priyanka and Katrina remains most anticipated. Cannes wraps: Mungiu's 'Fjord' takes Palme d'Or, Virginie Efira wins Best Actress. Meanwhile IMAX confirms Ranbir's 'Ramayana' and Yash's 'Toxic' for premium release.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, data centers. $50B Big Tech wave hits India. Iran deal 'largely negotiated' — Hormuz reopening could reshape India's entire energy import chain. Reliance-Adani rivalry intensifies.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chaired 40+ nation Hormuz summit with Macron. Hours later, Trump says deal 'largely negotiated.' Hormuz reopening would ease UK energy costs. Free summer bus travel for kids. Reform UK's Farage sharpens attacks as Iran crisis nears resolution.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga monitors Iran deal breakthrough — Hormuz reopening would transform global trade and energy flows for developing nations. India hosts Quad FM meeting May 26. Indian-American diaspora leaders at the helm of global economic governance.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
    ]

    data = {
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "posts": celeb_posts
    }
    with open(CELEB_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ celebrity-buzz.json: {len(celeb_posts)} posts updated")


if __name__ == "__main__":
    update_tech_buzz()
    update_celebrity_buzz()
    print("✅ All pulse data updated for 2026-05-23 23:00 PDT")
