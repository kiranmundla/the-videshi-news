#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-23 14:00 PDT"""

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
        # === TECH PULSE (14) ===
        "elonmusk": {
            "text": "SpaceX IPO projected at $1.25-2.2 trillion valuation — potentially the world's largest ever. Starship 12th test flight launches from Starbase, Texas. Meanwhile Nvidia CEO Jensen Huang says SpaceX rival in AI has 'largely conceded' China's chip market to Huawei.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-23",
        },
        "zuck": {
            "text": "Meta cuts 8,000 jobs and reassigns 7,000 to AI teams in massive restructuring. Leaked audio reveals Zuckerberg defended employee monitoring to win AI race. Tells surviving staff: 'I feel the weight of that' but signals no more company-wide layoffs in 2026. Threads crosses 150M daily active users.",
            "url": "https://x.com/zuck",
            "date": "2026-05-23",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI hard to challenge ChatGPT's dominance while navigating regulatory scrutiny over AI energy consumption. Gemini integration across Search, Workspace, and Cloud products accelerates as antitrust concerns mount.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-23",
        },
        "satyanadella": {
            "text": "Microsoft defends $80 billion AI infrastructure investment as Azure surpasses $75 billion in quarterly revenue. Plans $30 billion more in AI infrastructure spending next quarter. Copilot adoption across enterprise customers hits record highs.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-23",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 capabilities — 'smarter than the smartest person' — as the Musk v. OpenAI lawsuit over the $97.4 billion acquisition bid heads toward trial. OpenAI's valuation soars amid fierce competition with Meta, Google, and Anthropic.",
            "url": "https://x.com/sama",
            "date": "2026-05-23",
        },
        "tim_cook": {
            "text": "Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator, the heart to lead with integrity.' Apple asks Supreme Court to review App Store contempt ruling, calling spirit-based inquiry 'a recipe for abuse.'",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-23",
        },
        "nvidia": {
            "text": "Nvidia reports jaw-dropping $81.6 billion Q1 revenue — 10x from three years ago. Unveils Vera Rubin platform delivering 10x inference throughput per megawatt over Blackwell. CEO Huang sees $1 trillion in orders through next year. Concedes China AI chip market to Huawei amid US export restrictions.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-23",
        },
        "NandanNilekani": {
            "text": "Infosys co-founder's Fundamentum Partnership continues backing India's digital infrastructure startups as Big Tech pours $50 billion into India for AI, cloud, and digital infrastructure. India emerging as key AI talent hub.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-23",
        },
        "BillGates": {
            "text": "Bill Gates criticizes AI development pauses, argues stopping progress is counterproductive. Continues pushing global health initiatives through the Gates Foundation while maintaining skepticism toward cryptocurrency and NFTs.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-22",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise adoption of trustworthy Generative AI using the watsonx platform, targeting hybrid and on-premises environments.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-23",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO continues integrating generative AI across Creative Cloud and Experience Cloud as competition intensifies in AI creative tools space. Adobe's Firefly family of models gaining traction against Midjourney and DALL-E.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-22",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal maintains low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley's startup ecosystem.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair continues leading luxury fashion's digital transformation at Cannes 2026, balancing haute couture heritage with AI-enabled personalization and sustainability commitments.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-22",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates complex global logistics landscape as US tariff policies reshape supply chains. FedEx AI-powered route optimization and autonomous delivery pilots expanding across major US metros.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-23",
        },

        # === INDIA PULSE (12) ===
        "narendramodi": {
            "text": "PM Modi distributes 51,000+ appointment letters at 19th Rozgar Mela, emphasizing youth role in India's growth through semiconductors, AI, and green tech. Meets US Secretary of State Rubio — invited to White House. Italy visit includes bilateral with Meloni; viral 'Melody' candy gift sparks stock rally.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-23",
        },
        "PMOIndia": {
            "text": "19th Rozgar Mela: 51,000+ appointment letters distributed across 47 locations. PM-Rubio bilateral focuses on energy, trade, Indo-Pacific security. Quad Foreign Ministers meeting in New Delhi confirmed for May 26.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-23",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah oversees security preparations as US Secretary of State Rubio's four-day India visit begins. Internal security framework and border modernization programs continue across northeast India.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-23",
        },
        "RahulGandhi": {
            "text": "Rahul Gandhi warns of major economic crisis ahead, blames Modi government's policies for favoring Adani and Ambani while ordinary citizens face severe hardship. Criticizes focus on foreign tours over economic stabilization, urges Congress states to prepare for potential slowdowns.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-23",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath continues pushing the state's semiconductor and electronics manufacturing corridor. Rajasthan implements PM Modi's austerity measures — bans public-funded foreign travel and transitions to electric government vehicles.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-23",
        },
        "ArvindKejriwal": {
            "text": "Delhi CM Kejriwal's excise policy case continues to dominate political discourse. AAP leaders condemn legal proceedings as BJP conspiracy while the party focuses on governance reforms in Delhi and Punjab.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-23",
        },
        "DrSJaishankar": {
            "text": "India to host Quad Foreign Ministers meeting May 26 in New Delhi — Jaishankar to hold bilateral talks with Rubio (US), plus Australia and Japan counterparts. Key agenda: West Asia crisis, Strait of Hormuz, Indo-Pacific security, trade tariff resolution. PM Modi meeting arranged for Rubio.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-23",
        },
        "nsitharaman": {
            "text": "Finance Minister Sitharaman targets lower fiscal deficit for FY26, emphasizing structural reforms and fiscal discipline. India's GDP growth continues to outpace major economies as Big Tech invests $50 billion in Indian AI and cloud infrastructure.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-23",
        },
        "rashtrapatibhvn": {
            "text": "President of India observes ongoing national development milestones as Rozgar Mela reaches 19th edition with record 51,000 appointments. Constitutional and ceremonial functions continue as Rubio-Modi bilateral underscores India's growing geopolitical weight.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-23",
        },
        "gautam_adani": {
            "text": "Adani Group expands infrastructure portfolio as Rahul Gandhi renews attacks on Modi-Adani ties. Group continues aggressive push into green energy, ports, and data centers amid India's $50 billion Big Tech investment wave.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-23",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance announces major expansion into power and telecom sectors, leveraging the scrapped family noncompete agreement. Strategic investments in clean energy and infrastructure target energy-hungry India's growing demand.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-23",
        },
        "RNTata2000": {
            "text": "Ratan Tata Foundation continues philanthropic legacy through education, healthcare, and rural development initiatives. Tata Group's semiconductor fab plans align with India's chip manufacturing ambitions under PM Modi's vision.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-22",
        },

        # === WORLD / POWER PULSE (15) ===
        "realDonaldTrump": {
            "text": "Trump says Iran peace deal is 'largely negotiated' — will open Strait of Hormuz. 'Final aspects currently being discussed.' Claims 50/50 on deal at Rockland County rally, warns he may blast regime 'to kingdom come' if talks fail. Gulf nations and Pakistan push for permanent resolution.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-23",
        },
        "Keir_Starmer": {
            "text": "Starmer and Macron co-chair Paris meeting with 40+ countries on keeping Strait of Hormuz open post-Iran war. Announces free summer bus travel for children across England. Defends EU alignment plans using Henry VIII powers without parliamentary approval.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-23",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad Foreign Ministers meeting in New Delhi May 26, with Indo-Pacific security and China tensions on the agenda. Australia deepens defense partnerships with India and Japan.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-23",
        },
        "chrisluxonNZ": {
            "text": "NZ PM Luxon navigates trade impacts of global tariff realignment while strengthening Five Eyes and Indo-Pacific partnerships. New Zealand's border security receives fresh investment.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-22",
        },
        "HHShkMohd": {
            "text": "Dubai ruler Mohammed bin Rashid continues UAE's strategic positioning amid Gulf push for permanent Iran peace deal. UAE's role as diplomatic mediator gains prominence as Strait of Hormuz opening appears imminent.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-23",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni hosts PM Modi for bilateral in Rome — the viral 'Melody' candy exchange sparks global social media moment and stock rally. Italy deepens strategic partnership with India on defense, energy, and Mediterranean security.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-23",
        },
        "EmmanuelMacron": {
            "text": "Macron co-chairs 40+ nation meeting with Starmer in Paris on keeping Strait of Hormuz open after Iran conflict. France pushes for multilateral diplomatic solution alongside Gulf states. Cannes 2026 runs parallel to geopolitical maneuvering.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-23",
        },
        "WhiteHouse": {
            "text": "Secretary Rubio arrives in India for four-day visit (May 23-26) — first stop Kolkata, then New Delhi for Modi meeting. Quad FM meeting May 26. Rubio touts US energy exports to India. White House seeks to reset strained ties after tariff disputes.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-23",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy continues advocacy on AI regulation and government efficiency reform. Indian-American political figure's influence grows as US-India ties receive fresh attention during Rubio's India visit.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-23",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak navigates post-office political landscape as Conservative Party struggles with polling declines. Sunak's legacy on trade agreements and UK-India bilateral relations remains a reference point during Starmer's EU pivot.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-22",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance continues Indian-American community engagement as the Quad meeting in New Delhi puts US-India relations in the spotlight. Diaspora representation in the Trump administration at historic high.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-23",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel speaks at Bitcoin 2026 on 'Code is Free Speech: Ending the War on Bitcoin' alongside Acting AG Todd Blanche. Discusses federal policies impacting Bitcoin developers and open-source software rights.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-23",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan's role in shaping US AI policy draws attention as India's tech ecosystem receives $50B investment commitment. US-India tech corridor strengthens during Rubio visit.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-23",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman continues political commentary as Starmer faces pressure from Reform UK's Nigel Farage. Conservative opposition sharpens on EU alignment and immigration policy.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-22",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga navigates global development finance as Gulf nations push Iran peace deal and India hosts Quad meeting. Indian-American diaspora leaders increasingly shape international economic policy.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-23",
        },

        # === SPORTS PULSE (15) ===
        "imVkohli": {
            "text": "IPL 2026 playoffs heat up! RCB qualify despite 55-run loss to SRH (200/4 vs 255/4). Punjab Kings chase down LSG's 196/6 with 200/3. Next: MI vs RR at Wankhede tomorrow. Kohli's 14,000 T20 runs and 9th IPL hundred this season define an era. Playoffs in Dharamshala, Chandigarh, and Ahmedabad.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-23",
        },
        "ImRo45": {
            "text": "Mumbai Indians face Rajasthan Royals at Wankhede Stadium tomorrow in crucial IPL 2026 league match. Rohit Sharma's captaincy under scrutiny as MI's playoff chances hang by a thread. IPL final confirmed for Ahmedabad's Narendra Modi Stadium on May 31.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-23",
        },
        "msdhoni": {
            "text": "CSK legend Dhoni watches from the sidelines as IPL 2026 playoffs take shape. Punjab Kings stun Lucknow Super Giants, chasing 197 with 200/3. Four teams — RCB, GT, SRH, RR — locked on 18 points atop the table.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-23",
        },
        "Jaspritbumrah93": {
            "text": "Jasprit Bumrah's MI prepare for crucial Rajasthan Royals clash at Wankhede tomorrow. SRH's 255/4 against RCB showcases the firepower in IPL 2026 playoffs. Bumrah's death-overs mastery remains India's most valuable asset.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-23",
        },
        "hardikpandya7": {
            "text": "Hardik Pandya and MI face do-or-die situation against Rajasthan Royals at Wankhede May 24. IPL 2026 entering business end — Punjab Kings join the playoff conversation after chasing down LSG's 196/6 at Ekana Stadium.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-23",
        },
        "BCCI": {
            "text": "IPL 2026 playoffs confirmed: Dharamshala, New Chandigarh, and Ahmedabad host Qualifiers and Eliminator (May 26-31). Final at Narendra Modi Stadium, Ahmedabad. RCB, GT, SRH, RR top four with 18 points each. Punjab Kings beat LSG 200/3 chasing 196/6.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-23",
        },
        "ICC": {
            "text": "ICC watches IPL 2026 enter thrilling playoff phase as India's T20 ecosystem continues to set global cricket benchmarks. SRH's 255/4 one of the highest-ever IPL totals. Champions Trophy and T20 World Cup preparations continue in parallel.",
            "url": "https://x.com/ICC",
            "date": "2026-05-23",
        },
        "IPL": {
            "text": "IPL 2026 Match 68: Punjab Kings chase down 197, beating Lucknow Super Giants (200/3 vs 196/6) at Ekana Stadium. SRH beat RCB by 55 runs to confirm Qualifier 1 against GT. MI vs RR tomorrow at Wankhede. Final May 31 in Ahmedabad.",
            "url": "https://x.com/IPL",
            "date": "2026-05-23",
        },
        "Neeraj_chopra1": {
            "text": "Olympic champion Neeraj Chopra continues preparations for 2026 Diamond League circuit and World Athletics Championships. India's golden boy of athletics maintaining form ahead of key competitions.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-22",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu competes on the BWF World Tour as she maintains her status among the world's top shuttlers. Indian badminton continues its global rise with multiple players in world top 20.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Sania Mirza continues her post-retirement role as Indian tennis ambassador and mentor. Her commentary and analysis remain sought after during the French Open buildup at Roland Garros.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-21",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces pointed criticism from Russian GM Nepomniachtchi: 'Nearly every top Grandmaster would have a very good chance against him.' Gukesh takes classical chess break to prepare for title defense against Candidates winner Javokhir Sindarov later this year.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-23",
        },
        "chetrisunil11": {
            "text": "Indian football legend Sunil Chhetri's legacy continues to inspire as Indian Super League grows. India's FIFA World Cup qualification campaign remains a long-term aspiration for AIFF.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-22",
        },
        "sachin_rt": {
            "text": "Sachin Tendulkar watches son Arjun play for Lucknow Super Giants in IPL 2026. LSG fall short as Punjab Kings chase down 196/6 with 200/3. The Master Blaster's cricket legacy extends through the next generation.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-23",
        },
        "SGanguly99": {
            "text": "Former BCCI president Sourav Ganguly watches IPL 2026 playoffs unfold with KKR facing Delhi Capitals at Eden Gardens tomorrow. Kolkata's cricket heritage remains central to IPL's biggest moments.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-23",
        },
    }

    for handle, upd in updates.items():
        if handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            leader["latestPost"]["text"] = upd["text"]
            leader["latestPost"]["url"] = upd["url"]
            leader["latestPost"]["date"] = upd["date"]
            updated += 1
        else:
            print(f"⚠️  Handle not found: {handle}")

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
            "caption": "IPL 2026 playoff drama! RCB qualify despite 55-run loss to SRH. Kohli's 14,000 T20 runs and 9th IPL hundred this season cement his GOAT status. Playoffs begin in Dharamshala — the King of cricket is ready for knockout stage.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi distributes 51,000+ appointment letters at Rozgar Mela, meets US Secretary Rubio who invites him to White House. Viral 'Melody' candy moment with Italian PM Meloni breaks the internet and moves stock markets.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Jensen Huang",
            "handle": "nvidia",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Nvidia's $81.6B Q1 revenue is 10x from three years ago. Vera Rubin platform delivers 10x inference per megawatt. Jensen sees $1 trillion in orders but concedes China market to Huawei. The leather jacket king of AI reigns supreme.",
            "url": "https://www.instagram.com/nvidia/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Trump declares Iran peace deal 'largely negotiated' — will open Strait of Hormuz. Says he's '50/50' on deal, warns of 'kingdom come' if talks fail. Gulf nations and Pakistan push for permanent resolution as global oil markets watch.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX files for potentially the world's largest IPO at $1.25-2.2 trillion valuation. Starship 12th test flight launches. The world's first trillionaire keeps pushing the boundaries of space, AI, and electric vehicles.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 8,000 jobs cut, 7,000 reassigned to AI. Leaked audio shows Zuck defending employee monitoring for AI race. 'Success isn't a given.' Threads hits 150M daily users. No more company-wide layoffs this year — for now.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat from Russian GM Nepomniachtchi: 'Every top GM would have a good chance against him.' Gukesh takes classical break to prepare for title defense against Candidates winner Sindarov later this year. The youngest world champion plots his comeback.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands aggressively into power and telecom sectors after scrapping family noncompete agreement. Strategic investments in clean energy and infrastructure target India's explosive demand growth.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Captain Cool watches from the sidelines as IPL 2026 enters its thrilling playoff phase. Arjun Tendulkar plays for LSG as next-gen cricketers carry forward legends' legacy. Punjab Kings stun Lucknow in dramatic chase.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer Singh's post-apocalyptic thriller 'Pralay' begins filming August 2026 with a massive ₹300 crore budget. Meanwhile Vicky Kaushal blocks 18 months for 'Mahavatar' (Parashurama epic). Bollywood bets big on ambitious storytelling.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' — Shah Rukh Khan's ₹350 crore action thriller with daughter Suhana Khan and Deepika Padukone — confirmed for December 24, 2026 release. Directed by Siddharth Anand. Bollywood's biggest Christmas release ever.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika Padukone stars alongside Shah Rukh Khan and Suhana Khan in 'King' — the ₹350 crore action thriller slated for Christmas 2026. One of Bollywood's most bankable stars continues to command the box office.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chairs 40+ nation Paris meeting with Macron on keeping Strait of Hormuz open. Announces free summer bus travel for kids across England. Defends EU alignment plans as Reform UK's Farage circles for the kill.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI face do-or-die clash against Rajasthan Royals at Wankhede tomorrow. IPL 2026 entering business end with four teams locked on 18 points. Hardik's all-round abilities will be tested in the pressure cooker.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit Dosanjh's concert tour continues to sell out across North America — Vancouver the latest stop. The Punjabi superstar has become the face of Indian music going global, bridging Bollywood and the diaspora.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, and data centers as $50B Big Tech investment wave hits India. Faces renewed political attacks from Rahul Gandhi over Modi-Adani ties. The infrastructure empire keeps growing.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra continues her Hollywood-Bollywood dual career. Cannes 2026 brings fresh red carpet moments while her production slate grows. The ultimate NRI success story.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia Bhatt's 2026 slate includes multiple high-profile projects as she cements her position as Bollywood's most bankable actress. 'Jee Le Zaraa' with Priyanka and Katrina remains one of the most anticipated films.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shraddha Kapoor shares mountain retreat moments as she takes a break between projects. Instagram's most-followed Indian actress continues to dominate social media with her relatable content style.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sacaborstendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "The Master Blaster watches son Arjun play for Lucknow Super Giants in IPL 2026. LSG fall short as Punjab Kings chase down 196/6. Cricket's greatest legacy extends to the next generation on the biggest stage.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga shapes global development policy as India hosts Quad meeting and Iran peace deal takes shape. Indian-American diaspora leaders increasingly influential in international economic governance.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Travis Head",
            "handle": "travishead34",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SRH smash RCB for 255/4 in IPL 2026 with Ishan Kishan (79), Abhishek Sharma (56), Heinrich Klaasen (51) leading the charge. The Australian's IPL stint adds to his growing T20 reputation.",
            "url": "https://www.instagram.com/travishead34/",
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
    print("✅ All pulse data updated for 2026-05-23 14:00 PDT")
