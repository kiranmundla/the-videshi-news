#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-23 20:00 PDT
Key updates this cycle:
- PBKS beat LSG by 7 wickets (Shreyas Iyer 101*), PBKS at 15 pts in 4th
- Tomorrow's double-header decides 4th playoff spot: MI vs RR + KKR vs DC
- Kohli-Head handshake snub goes viral globally
- Trump says Iran decision by Sunday — '50/50' deal vs resuming war
- Kevin Warsh sworn in as 17th Fed Chair on May 22
- Dow at ~50,563 record territory
- Cannes 2026: Aishwarya Rai Bachchan dazzles with Aaradhya
- Meta layoffs: 15,000 total (8K cut + 7K to AI)
- SpaceX IPO: JPMorgan targets $1.75T valuation
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
            "text": "SpaceX IPO filing targets $1.75 trillion valuation per JPMorgan — S&P 500 inclusion could force $950B in passive fund reallocation. Starship completes 12th test flight from Starbase. The world's richest person pushes SpaceX toward what could be the largest public offering in history.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-23",
        },
        "zuck": {
            "text": "Meta confirms 15,000 total job actions — 8,000 cut, 7,000 reassigned to AI teams. Spending $115-135 billion on AI infrastructure in 2026. Leaked audio: Zuckerberg defended employee surveillance to win the AI race. Employees 'miserable' per NYT. Threads crosses 150M daily users.",
            "url": "https://x.com/zuck",
            "date": "2026-05-23",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI across Search, Workspace, and Cloud. Antitrust concerns mount. Quad FM meeting in New Delhi on May 26 puts Indo-Pacific tech cooperation in focus — Google's India investments under the spotlight as Big Tech pours $50B into India.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-23",
        },
        "satyanadella": {
            "text": "Microsoft defends $80B AI infrastructure investment as Azure crosses $75B quarterly revenue. Plans $30B more next quarter. Copilot enterprise adoption at record highs. The AI arms race between Microsoft, Google, and Meta intensifies ahead of WWDC 2026.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-23",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 — 'smarter than the smartest person' — as Musk v. OpenAI lawsuit heads toward trial. OpenAI's valuation soars. Bill Gates argues AI development pauses are counterproductive. The race for AGI enters its most intense phase yet.",
            "url": "https://x.com/sama",
            "date": "2026-05-23",
        },
        "tim_cook": {
            "text": "Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator.' Apple asks Supreme Court to review App Store contempt ruling. Firefly-competitive AI features set for WWDC 2026 as Apple plays catch-up in generative AI.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-23",
        },
        "nvidia": {
            "text": "Nvidia posts jaw-dropping $81.6B Q1 revenue — 10x from three years ago. Unveils Vera Rubin platform: 10x inference throughput per megawatt over Blackwell. Dow hits record ~50,563. CEO Huang sees $1 trillion in orders but concedes China market to Huawei amid US export controls.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-23",
        },
        "NandanNilekani": {
            "text": "Big Tech pours $50 billion into India for AI, cloud, and digital infrastructure. Infosys co-founder's Fundamentum Partnership continues backing India's digital startups. Quad FM meeting May 26 will discuss critical tech partnerships — India emerges as key AI talent hub.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-23",
        },
        "BillGates": {
            "text": "Bill Gates criticizes AI development pauses — argues stopping progress is counterproductive and risks ceding ground to less safety-conscious actors. Global health initiatives via the Gates Foundation continue. Kevin Warsh, whom Gates has advised, takes the Fed chair.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-23",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise Generative AI adoption using watsonx platform. India emerging as major enterprise AI deployment hub as $50B Big Tech investment wave lands.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-23",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO continues integrating generative AI across Creative Cloud and Experience Cloud. Firefly models gain traction against Midjourney and DALL-E. Competition intensifies as Meta, Google, and Adobe race to dominate the creator economy.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-23",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal maintains low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley. The Indian-American tech diaspora continues shaping global AI leadership.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair steers the luxury house through a competitive landscape. Cannes 2026 puts Chanel back in the spotlight as Aishwarya Rai Bachchan dazzles on the red carpet. Indian-born diaspora influence in global luxury leadership continues to grow.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-23",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates global logistics amid trade disruptions and shifting supply chains. Indian-American CEO exemplifies diaspora leadership at a Fortune 50 company reshaping last-mile delivery with AI and automation.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-23",
        },

        # === INDIA PULSE ===
        "narendramodi": {
            "text": "PM Modi hosts US Secretary of State Rubio in New Delhi — wide-ranging talks on trade, defense, energy, and Indo-Pacific security. Rubio invites Modi to White House. Quad FM Meeting on May 26 in Delhi with Australia and Japan FMs. India positioned as key player in Iran peace framework.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-23",
        },
        "PMOIndia": {
            "text": "India-US bilateral ties deepen as Rubio's 4-day India visit sets stage for Quad FM meeting May 26. Modi-Rubio talks cover defense cooperation, critical tech, energy security, and West Asia situation. India faces $22.2B in FPI outflows and rupee near ₹94.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-23",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah oversees national security preparations as US Secretary of State Rubio visits India ahead of Quad FM meeting. Internal security and counter-terrorism cooperation remain key bilateral agenda items.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-23",
        },
        "RahulGandhi": {
            "text": "Congress leader Rahul Gandhi renews attacks on Modi-Adani ties as Adani Group expands into power, telecom, and green energy. Opposition sharpens criticism amid $50B Big Tech investment wave and $22.2B FPI outflow concerns.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-23",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath continues aggressive infrastructure push in India's most populous state. UP positions itself as key destination for Big Tech's $50B India investment wave in AI and data centers.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-23",
        },
        "ArvindKejriwal": {
            "text": "AAP leader Kejriwal steps up opposition rhetoric. Delhi politics intensifies as national attention pivots between Iran deal, Rubio's India visit, $22.2B FPI outflows, and the approaching Quad FM meeting.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-23",
        },
        "DrSJaishankar": {
            "text": "EAM Jaishankar holds strategic talks with US Secretary of State Rubio ahead of Quad FM Meeting on May 26 in New Delhi. Agenda: Indo-Pacific, West Asia crisis, defense, energy, critical tech. Australia and Japan FMs also calling on PM Modi. India's global diplomatic moment.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-23",
        },
        "nsitharaman": {
            "text": "Finance Minister Sitharaman monitors India's economic outlook as $50B in Big Tech investments land while FPI outflows hit $22.2B and rupee weakens near ₹94. Kevin Warsh takes over as Fed Chair — markets watch for rate signals.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-23",
        },
        "rashtrapatibhvn": {
            "text": "President Droupadi Murmu presides over the constitutional framework as India hosts critical Quad diplomacy. The nation's global standing strengthens with US, Japan, and Australia deepening Indo-Pacific cooperation through Delhi.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-23",
        },
        "gautam_adani": {
            "text": "Adani Group pushes into green energy, ports, and data centers as India attracts $50B in Big Tech investments. Reliance-Adani rivalry intensifies after Ambani scraps family noncompete. Faces renewed political attacks from Rahul Gandhi over Modi-Adani ties.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-23",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands into power and telecom after scrapping family noncompete. $1B telecom infrastructure investment, clean energy push, shares up 4.9%. The Ambani-Adani duopoly reshapes India's corporate landscape amid record Big Tech inflows.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-23",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its legacy of philanthropy and nation-building. Tata Group companies remain at the forefront as India attracts record foreign investment in AI and digital infrastructure.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-22",
        },

        # === WORLD / POWER PULSE ===
        "realDonaldTrump": {
            "text": "Trump tells Axios he'll decide by SUNDAY whether to sign the Iran deal or resume war — '50/50' on peace vs 'blowing them to kingdom come.' MoU fine-tuned with Pakistan mediating. Calls Gulf allies, meets Witkoff and Kushner. VP Vance returns to DC. Tulsi Gabbard exits as DNI.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-23",
        },
        "WhiteHouse": {
            "text": "White House in crisis mode on Iran — Trump gives Sunday deadline for deal decision. 14-point MoU with Pakistan mediating. Tulsi Gabbard forced to resign as DNI (husband's cancer); Aaron Lukas named acting director. Kevin Warsh sworn in as 17th Fed Chair at White House ceremony.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-23",
        },
        "Keir_Starmer": {
            "text": "UK PM Starmer co-chairs 40+ nation Paris meeting with Macron on Strait of Hormuz security. Announces free summer bus travel for kids. Defends EU alignment as Reform UK's Farage circles. Trump's Sunday Iran deadline raises stakes for global energy security.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-23",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosts 40+ nation Paris summit on Strait of Hormuz security with UK's Starmer. France at the center of Iran peace effort. Oil at $106.92. Trump's Sunday deadline on the Iran deal keeps European energy markets on edge.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-23",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad FM meeting in New Delhi on May 26. Indo-Pacific security, technology cooperation, and maritime stability top the agenda. Trump's Sunday Iran deadline adds urgency to Quad energy and security discussions.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-23",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni's viral 'Melody' candy moment with Modi strengthens Italy-India ties. Europe watches Trump's Sunday Iran deadline — Hormuz reopening would ease energy costs. G7 coordination on Iran response intensifies.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-23",
        },
        "HHShkMohd": {
            "text": "UAE ruler Mohammed bin Rashid watches Iran deal developments closely as Trump sets Sunday deadline. Gulf nations push for permanent Hormuz resolution. Oil at $106.92 — the Gulf's role as trade hub depends on stable maritime passage.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-23",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Luxon monitors Indo-Pacific developments as Quad FM meeting approaches May 26. Five Eyes alignment and Pacific security key NZ priorities amid Trump's Sunday Iran deadline and shifting US-China dynamics.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-23",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy continues post-DOGE political trajectory. Gabbard's forced resignation as DNI makes him the highest-profile Indian-American to have served and departed Trump's inner circle. His Ohio political ambitions and 'anti-woke' brand remain active.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-23",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak observes from opposition as Starmer navigates Iran, EU alignment, and Reform UK's rise. Sunak's legacy as Britain's first Indian-origin PM continues to resonate with the global diaspora.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-23",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance — Indian-American Yale Law grad — watches as VP JD Vance returns to DC for Iran deal deliberations. Trump's Sunday deadline on the Iran deal puts the entire national security team on high alert.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-23",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel continues reshaping the Bureau amid Gabbard's departure from DNI. Indian-American influence in national security deepens. Aaron Lukas named acting DNI. Trump's Sunday Iran deadline keeps the intelligence community in crisis mode.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-23",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan shapes US tech policy as Big Tech pours $50B into India and SpaceX files for a $1.75T IPO. Kevin Warsh takes the Fed chair. The Indian-American tech executive bridges Silicon Valley and DC at a pivotal moment.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-23",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman — Indian-origin Tory — remains vocal on immigration from the backbenches as Starmer faces pressure from Reform UK and the EU alignment debate.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-22",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga shapes global development policy as India hosts Quad FM meeting and Iran peace deal reaches Sunday deadline. Indian-American diaspora leaders increasingly drive international economic governance.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-23",
        },

        # === SPORTS PULSE ===
        "imVkohli": {
            "text": "CONTROVERSY: Kohli refuses handshake with Travis Head after SRH's 55-run win — video goes viral worldwide. Kohli gestured for Head to 'come bowl,' scored 15 before falling. RCB still finish TOP with 18 pts (best NRR). Qualifier 1 vs Gujarat Titans on May 27 at Dharamsala.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-23",
        },
        "ImRo45": {
            "text": "Mumbai Indians (4-9, eliminated) face Rajasthan Royals at Wankhede TOMORROW in the biggest spoiler match of IPL 2026. If MI beat RR, Punjab Kings (15 pts) take the 4th playoff spot. The final day's results reshape the entire playoff picture.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-23",
        },
        "msdhoni": {
            "text": "CSK eliminated from IPL 2026. Captain Cool watches as PBKS keep playoff hopes alive with Shreyas Iyer's stunning century (101* off ~55 balls). Tomorrow's double-header at Wankhede and Eden Gardens decides everything. The next generation plays on.",
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
            "text": "ICC board meeting in Ahmedabad May 30 to discuss playing conditions. IPL 2026 finale week: Kohli-Head handshake controversy dominates global cricket headlines. T20 World Cup squad selections create ripples — Bumrah, Shubman Gill left out for workload management.",
            "url": "https://x.com/ICC",
            "date": "2026-05-23",
        },
        "IPL": {
            "text": "TONIGHT: PBKS 200/3 beat LSG 196/6 by 7 wickets — Shreyas Iyer smashes maiden IPL century (101*). PBKS climb to 15 pts. TOMORROW decides it all: Match 69 MI vs RR (Wankhede), Match 70 KKR vs DC (Eden Gardens). Three teams, one spot. Playoffs start May 27.",
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
            "text": "Tennis icon Sania Mirza's legacy continues to inspire Indian tennis. Post-retirement, she remains the most prominent Indian face in global tennis, mentoring the next generation of players.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh takes a classical break to prepare for title defense against Candidates winner Sindarov. Russian GM Nepomniachtchi fires: 'Every top GM would have a good chance against him.' The youngest world champion plots his comeback.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-23",
        },
        "chetrisunil11": {
            "text": "AIFF announces 2026-27 Club Licensing results as Indian football restructures. Sunil Chhetri's legacy as India's all-time top scorer endures — the next generation looks to carry the torch he lit.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-23",
        },
        "sachin_rt": {
            "text": "The Master Blaster watches son Arjun play for LSG in IPL 2026. PBKS chased down LSG's 196/6 tonight — Shreyas Iyer's 101* seals a stunning 7-wicket win. Cricket's greatest legacy extends to the next generation on the biggest stage.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-23",
        },
        "SGanguly99": {
            "text": "Former BCCI president Saurav Ganguly watches IPL 2026's thrilling final weekend. KKR — the franchise he built — face DC at Eden Gardens TOMORROW in a do-or-die battle for the 4th playoff spot. Need to win AND hope RR lose. The Dada legacy looms large.",
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
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "HANDSHAKE GATE: Kohli refuses Travis Head's handshake — video goes viral globally. Kohli gestured for Head to bowl, scored 15, then walked past him post-match. RCB still TOP with 18 pts. Qualifier 1 vs GT on May 27. Tomorrow's double-header decides the 4th playoff spot.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi hosts US Secretary of State Rubio — talks on trade, defense, energy, Indo-Pacific. Rubio invites Modi to White House. Quad FM meeting May 26 in Delhi. India faces $22.2B FPI outflows and rupee near ₹94 — but Big Tech pouring $50B into India's digital future.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MAIDEN IPL CENTURY! Shreyas Iyer smashes 101* as PBKS chase down LSG's 196/6 with 7 wickets and 2 overs to spare. Punjab climb to 15 pts in 4th. Now they need MI to beat RR AND KKR to lose to DC tomorrow. The most dramatic IPL final day in years.",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborofficial",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Aishwarya dazzles at Cannes 2026 in Amit Aggarwal's sculptural 'Luminara' couture — 1,500 hours of craftsmanship. Daughter Aaradhya joins her on the red carpet in ruby-red. 24th Cannes appearance. ₹5 crore necklace. L'Oréal Lights on Women's Worth Gala celebrates women in cinema.",
            "url": "https://www.instagram.com/aaborofficial/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Trump sets SUNDAY DEADLINE on Iran deal — '50/50' between signing or 'blowing them to kingdom come.' 14-point MoU fine-tuned with Pakistan mediating. Calls Gulf allies. Tulsi Gabbard exits as DNI. VP Vance returns to DC. Kevin Warsh sworn in as Fed Chair.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX files for potentially the world's LARGEST IPO ever — JPMorgan targets $1.75T valuation. S&P 500 inclusion could trigger $950B passive fund reallocation. Starship's 12th test flight from Starbase. Meanwhile Dow hits record ~50,563.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 15,000 total job actions (8K cut + 7K reassigned). Spending $115-135B on AI infra in 2026. Leaked audio: Zuck defends surveillance for AI race. NYT: employees 'miserable.' Threads hits 150M daily users. 'Success isn't a given.'",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat — GM Nepomniachtchi: 'Every top GM would have a good chance against him.' Gukesh takes classical break to prepare for title defense against Sindarov. The youngest world champion plots his comeback.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "CSK eliminated from IPL 2026 playoffs. Captain Cool watches as Shreyas Iyer hits 101* for PBKS in a 7-wicket demolition of LSG. Tomorrow's double-header decides the 4th spot — three teams, one seat. The IPL Dhoni helped build has never been more dramatic.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' — SRK's ₹350 crore action thriller with Suhana and Deepika — may split into two parts. Part 1 reportedly eyed for September 2026. Directed by Siddharth Anand. Meanwhile KKR face DC at Eden Gardens tomorrow — SRK's team needs a miracle to make playoffs.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika uses body double for action in SRK's 'King' and Atlee's 'Raka' due to pregnancy. Ranveer and Deepika back from her birthday trip in New York. Meanwhile Aishwarya stuns Cannes with daughter Aaradhya on the red carpet.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI face Rajasthan Royals at Wankhede TOMORROW — MI's dead rubber is RR's knockout. If MI win, PBKS (15 pts) get the 4th spot. Hardik's MI can play kingmaker on the most dramatic final day in IPL history. Three teams' fates in MI's hands.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit's concert tour continues selling out across North America — Vancouver the latest stop. The Punjabi superstar is THE face of Indian music going global, bridging Bollywood and the diaspora one sold-out arena at a time.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment, clean energy push, shares up 4.9%. India attracts $50B Big Tech wave while facing $22.2B FPI outflows. The Ambani-Adani duopoly reshapes India Inc.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra's dual Hollywood-Bollywood career continues. 'Jee Le Zaraa' with Katrina and Alia remains most anticipated. Cannes 2026 puts Indian celebrities front and center — Aishwarya and Aaradhya steal the red carpet.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer's post-apocalyptic thriller 'Pralay' begins filming August 2026 — ₹300 crore budget. Back from Deepika's birthday trip in New York. Meanwhile Vicky Kaushal blocks 18 months for 'Mahavatar.' Bollywood bets big on 2026-27.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PBKS chase down LSG's 196/6 tonight — Shreyas Iyer's 101* seals it. Son Arjun played for LSG this IPL. Cricket's greatest legacy extends to the next generation. Tomorrow's final day: MI vs RR + KKR vs DC. Three teams, one spot.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's live album generates buzz as her US tour hits 5 cities. The voice of a generation continues selling out venues across the diaspora — bringing Bollywood's golden age of playback singing to NRI audiences worldwide.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress (90M+) shares mountain retreat moments between projects. Shraddha's relatable content style continues to dominate social media while Cannes 2026 puts Bollywood glamour on the global stage.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia's 2026 slate packed with high-profile projects. 'Jee Le Zaraa' with Priyanka and Katrina remains one of the year's most anticipated films. Cannes 2026 and Alia's appearances spark fan debates with Aishwarya loyalists online.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chairs 40+ nation Paris meeting with Macron on Strait of Hormuz. Free summer bus travel for kids. Trump's Sunday Iran deadline raises UK energy security stakes. Reform UK's Farage sharpens attacks as Starmer juggles domestic and global crises.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, data centers. $50B Big Tech wave hits India. Reliance-Adani rivalry intensifies. Rahul Gandhi renews political attacks. Kevin Warsh takes Fed chair — global capital flows to watch for India impact.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga shapes global development policy as India hosts Quad FM meeting and Trump sets Sunday Iran deadline. Indian-American diaspora leaders drive international economic governance at the highest levels.",
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
    print("✅ All pulse data updated for 2026-05-23 20:00 PDT")
