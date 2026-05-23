#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-23 08:00 PDT"""

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
            "text": "SpaceX files for potentially the world's largest IPO at $1.25 trillion valuation. Meanwhile Nvidia CEO Jensen Huang says the company has 'largely conceded' China's AI chip market to Huawei as US export restrictions reshape the global semiconductor landscape.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-23",
        },
        "zuck": {
            "text": "\"Success isn't a given. AI is the most consequential technology of our lifetimes.\" Meta cuts 8,000 jobs in AI-driven restructuring as Zuckerberg tells employees he 'feels the weight' of layoffs. Also hiring a 'beach water person' for his Hawaii estate.",
            "url": "https://x.com/zuck",
            "date": "2026-05-22",
        },
        "sundarpichai": {
            "text": "Google CEO continues pushing Gemini AI to challenge ChatGPT while managing fallout from 12,000+ job cuts. Google's energy consumption for AI operations drawing increased scrutiny from regulators.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-22",
        },
        "satyanadella": {
            "text": "Microsoft defends $80 billion AI and cloud infrastructure investment as Azure surpasses $75 billion in quarterly revenue. Plans $30 billion more in AI infrastructure spending next quarter.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-22",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 capabilities — 'smarter than the smartest person' — as the ongoing Musk v. OpenAI lawsuit heads toward trial over the $97.4 billion acquisition bid.",
            "url": "https://x.com/sama",
            "date": "2026-05-22",
        },
        "tim_cook": {
            "text": "Tim Cook's Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator, the heart to lead with integrity.' Apple asks Supreme Court to review App Store contempt ruling, calling spirit-based inquiry 'a recipe for abuse.'",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-22",
        },
        "nvidia": {
            "text": "Nvidia reports jaw-dropping $82 billion Q1 revenue — 10x from three years ago. CEO Jensen Huang unveils Vera CPU, opening a 'brand new $200 billion TAM' for agentic AI. Calls stock stagnation 'one of the mysteries of the universe.' Concedes China AI chip market to Huawei.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-23",
        },
        "NandanNilekani": {
            "text": "Infosys co-founder Nandan Nilekani's Fundamentum Partnership continues backing India's digital infrastructure startups as Big Tech pours $50 billion into India for AI, cloud, and digital infrastructure.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-21",
        },
        "BillGates": {
            "text": "Bill Gates criticizes AI development pauses, argues stopping progress is counterproductive. Continues skepticism toward cryptocurrency and NFTs while pushing global health initiatives through the Gates Foundation.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-21",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise adoption of trustworthy Generative AI using the watsonx platform, targeting hybrid and on-premises environments.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-20",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO Shantanu Narayen continues integrating generative AI across Creative Cloud and Experience Cloud as the company navigates the competitive AI landscape in creative tools.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-20",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal keeps a low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley's startup ecosystem.",
            "url": "https://x.com/paraga",
            "date": "2026-05-19",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair leads the luxury maison through transformation, balancing traditional craftsmanship with digital innovation and sustainability goals.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-19",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam drives the company's AI-powered logistics transformation, leveraging automation and data analytics to reshape global supply chain operations.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-19",
        },

        # === WORLD / POWER PULSE (15) ===
        "realDonaldTrump": {
            "text": "Trump digs in on $1.8 billion 'anti-weaponization' fund amid GOP backlash. Praises Palantir on Truth Social after records show he bought the stock. Posts AI video of throwing Stephen Colbert in dumpster. Skips Don Jr.'s Bahamas wedding citing 'love for the United States.'",
            "url": "https://truthsocial.com/@realDonaldTrump",
            "date": "2026-05-23",
        },
        "Keir_Starmer": {
            "text": "UK PM announces free summer bus travel for children across England. Co-chairs Paris meeting with Macron on Hormuz Strait access. Congratulates Arsenal on Premier League title. Defends plan to align with EU rules via Henry VIII powers.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-22",
        },
        "AlboMP": {
            "text": "Australian PM Anthony Albanese prepares for Quad Foreign Ministers meeting in New Delhi on May 26, with Indo-Pacific security and strategic partnership on the agenda.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-22",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Christopher Luxon focuses on domestic policy reforms while maintaining engagement with Pacific and Five Eyes partners on security and trade.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-20",
        },
        "HHShkMohd": {
            "text": "UAE Vice President Sheikh Mohammed bin Rashid continues driving Dubai's tech and economic transformation agenda, with focus on AI adoption and smart city initiatives.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-20",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Giorgia Meloni hosts PM Modi for bilateral talks in Rome, strengthening India-Italy ties on trade, defense, and technology cooperation during Modi's European tour.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-23",
        },
        "EmmanuelMacron": {
            "text": "President Macron co-chairs Paris meeting with UK PM Starmer on maintaining Hormuz Strait access post-Iran conflict. 40+ countries attend. Polymarket gives 44% probability of Trump-Macron call in May.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-22",
        },
        "WhiteHouse": {
            "text": "White House launches AI.Gov website to strengthen U.S. leadership in artificial intelligence. The initiative highlights the administration's commitment to advancing AI through strategic efforts and regulatory frameworks.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-22",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy and Elon Musk expose rift with MAGA loyalists over immigrant tech workers, criticizing a culture that prioritizes mediocrity over excellence. H-1B visa debate intensifies in Silicon Valley.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-21",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak remains active in Conservative politics, focusing on trade policy and UK's post-Brexit tech strategy as the party navigates opposition.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-20",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance, Indian-American lawyer and Yale Law graduate, continues her public advocacy for education and judicial reform from the White House.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-20",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel continues 'anti-weaponization' agenda as Trump defends $1.8 billion fund amid bipartisan scrutiny and ongoing federal law enforcement reform.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-22",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan works on strengthening India-US strategic ties ahead of the AI Impact Summit 2026. Focus on semiconductors, electronics manufacturing, and supply chain resilience.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-21",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman remains vocal on immigration and security policy as Nigel Farage's Reform UK gains momentum ahead of the 2028 London mayoral race.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-20",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga unveils crisis toolkit allowing countries to access $60-100 billion. Backs 'Small AI' for farmers and rural communities at ATX Singapore 2026 — a farmer in UP shares crop disease photo, gets instant diagnosis.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-22",
        },

        # === INDIA PULSE (12) ===
        "narendramodi": {
            "text": "PM Modi visits Italy for bilateral talks with Cyprus President Christodoulides and Italian PM Meloni in Rome. 'Melody' candy gift goes viral. India to host Quad Foreign Ministers meet in New Delhi on May 26.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-23",
        },
        "PMOIndia": {
            "text": "PMO confirms India will host Quad Foreign Ministers meeting on May 26 in New Delhi. PM Modi meets Big Tech CEOs who commit $50 billion for AI, cloud, and digital infrastructure in India over 5-7 years.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-23",
        },
        "AmitShah": {
            "text": "BJP files FIR against Rahul Gandhi for calling PM Modi and Home Minister Amit Shah 'traitors' during a public event. Karnataka BJP chief demands apology, warns of statewide protests.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-22",
        },
        "RahulGandhi": {
            "text": "Congress leader Rahul Gandhi faces FIR over 'traitors' remark against PM Modi and Amit Shah during Raebareli speech. Accuses government of economic mismanagement, inflation, and constitutional erosion.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-22",
        },
        "myogiadityanath": {
            "text": "Yogi Adityanath's UP government announces 2% DA hike to 60%, providing relief to 16 lakh government employees, teachers, and pensioners amid rising inflation pressure.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-22",
        },
        "ArvindKejriwal": {
            "text": "AAP's Arvind Kejriwal continues navigating legal challenges while maintaining his push for urban governance reforms and anti-corruption agenda in Delhi politics.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-20",
        },
        "DrSJaishankar": {
            "text": "India to host Quad Foreign Ministers meeting in New Delhi on May 26. External Affairs Minister Jaishankar will hold bilateral meetings with counterparts from Australia, Japan, and the US amid the widening West Asia crisis.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-23",
        },
        "nsitharaman": {
            "text": "Finance Minister Nirmala Sitharaman's Budget 2026 team revealed — experienced IAS officers and experts in expenditure, revenue, and economic affairs ensuring robust fiscal planning amid global uncertainties.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-22",
        },
        "rashtrapatibhvn": {
            "text": "The President of India continues constitutional duties as the nation prepares for major diplomatic engagements including the Quad Foreign Ministers meet on May 26.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-20",
        },
        "gautam_adani": {
            "text": "Gautam Adani overtakes Mukesh Ambani as Asia's richest man. Adani Group and Reliance now collaborating in fuel retail, aiming to strengthen market positions through strategic partnerships.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-22",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani meets Nvidia CEO Jensen Huang at AI Summit to discuss AI advancements and future collaborations. Reliance expanding into power and telecom sectors with ambitious new investments.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-22",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its philanthropic mission across healthcare, education, and rural development as Tata Group companies maintain diversified global operations.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-20",
        },

        # === SPORTS PULSE (15) ===
        "imVkohli": {
            "text": "Virat Kohli's handshake snub of Travis Head after RCB vs SRH goes viral — taunted Head as 'impact player.' First Indian to 14,000 T20 runs. Scored 9th IPL hundred this season. RCB secure playoff spot.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-23",
        },
        "ImRo45": {
            "text": "Mumbai Indians eliminated from IPL 2026 playoffs after inconsistent campaign. Captain Rohit Sharma's side suffered another top-order collapse in loss to KKR at Eden Gardens.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-22",
        },
        "msdhoni": {
            "text": "MS Dhoni didn't play a single game in IPL 2026 — sidelined by calf strain and thumb injury. CSK eliminated after 89-run loss to GT. 'If he knows it is not right, he won't play' says coach. IPL future uncertain at 44.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-23",
        },
        "Jaspritbumrah93": {
            "text": "Jasprit Bumrah emerges as potential MI captain after Hardik Pandya's difficult season. Sanjay Manjrekar backs Bumrah's leadership credentials. Recently led MI to crucial win against PBKS.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-22",
        },
        "hardikpandya7": {
            "text": "Hardik Pandya fined 10% of match fee for 'abuse of cricket equipment' — knocked bails off stumps in frustration during KKR loss. A forgettable IPL 2026: 172 runs, 4 wickets in 9 matches. MI captaincy under scrutiny.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-22",
        },
        "BCCI": {
            "text": "BCCI to decide IPL 2026 playoff venues in a day or two — Mullanpur and Bengaluru as potential sites. Season runs through May 31. Four teams fighting for one remaining playoff spot.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-23",
        },
        "ICC": {
            "text": "ICC President Jay Shah targets making women's cricket the most popular sport in the world. PCB engages ICC on visa issues preventing Pakistani players from joining IPL.",
            "url": "https://x.com/ICC",
            "date": "2026-05-22",
        },
        "IPL": {
            "text": "IPL 2026 playoff race reaches boiling point: RCB, GT, SRH through. One spot remains — PBKS, RR, KKR, DC in contention. CSK, MI, LSG eliminated. GT crush CSK by 89 runs in decisive Match 66.",
            "url": "https://x.com/IPL",
            "date": "2026-05-23",
        },
        "Neeraj_chopra1": {
            "text": "Olympic champion Neeraj Chopra continues his javelin season preparation. India's first individual Olympic gold medalist remains the face of Indian athletics on the global stage.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-20",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu, India's badminton queen with two Olympic medals, continues her competitive season aiming to maintain her world ranking and defend her legacy.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-20",
        },
        "MirzaSania": {
            "text": "Sania Mirza stays active in tennis commentary and mentoring young Indian players following her retirement from professional tennis.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-19",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces criticism from Nepomniachtchi: 'Nearly every top Grandmaster would have a good chance in a match against him.' Nepo says Gukesh's post-Candidates form has been 'disturbing for fans.'",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-23",
        },
        "chetrisunil11": {
            "text": "India football legend Sunil Chhetri continues his mentoring role for the next generation of Indian footballers as the ISL 2025-26 season reaches its conclusion.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-20",
        },
        "sachin_rt": {
            "text": "Sachin Tendulkar watches IPL 2026 as son Arjun Tendulkar makes debut for Lucknow Super Giants. The Master Blaster remains cricket's most iconic figure.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-22",
        },
        "SGanguly99": {
            "text": "Former BCCI President Sourav Ganguly remains a prominent voice in Indian cricket, offering commentary on IPL 2026's dramatic playoff race and the future of Team India.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-21",
        },
    }

    for handle, update in updates.items():
        leader = leaders_by_handle.get(handle)
        if leader:
            leader["latestPost"] = {
                "url": update["url"],
                "text": update["text"],
                "date": update["date"],
                "likes": 0,
                "retweets": 0,
            }
            updated += 1
        else:
            print(f"  WARNING: Handle @{handle} not found in tech-buzz.json")

    data["lastUpdated"] = datetime.now(timezone.utc).isoformat()
    with open(TECH_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {updated}/{len(updates)} leaders in tech-buzz.json")


def update_celebrity_buzz():
    with open(CELEB_BUZZ) as f:
        data = json.load(f)

    celeb_updates = [
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "First Indian batter to 14,000 T20 runs! 9th IPL hundred this season. Handshake snub of Travis Head goes viral. RCB through to playoffs.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Dhurandhar Raw & Undekha streaming on Netflix May 22! Pralay shoot begins August 2026 with Rs 300 crore budget. Dhurandhar heading to Japan July 10.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "KING locked for Christmas 2026! December 24 release confirmed. Deepika Padukone and Suhana Khan co-star in Siddharth Anand's action thriller. Rs 350 crore budget.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Co-starring with SRK in King this Christmas 2026. Siddharth Anand directs this action thriller with Rs 350 crore budget.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Set to star as a lawyer in a dynamic new Hollywood film. Priyanka continues bridging Bollywood and Hollywood with powerful roles.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-21"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Dil-Luminati Tour continues across North America! Sold-out shows in Shreya Ghoshal's competition. The Punjabi King keeps breaking records globally.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Fined 10% match fee for 'abuse of cricket equipment' in KKR loss. A tough IPL 2026: 172 runs, 4 wickets in 9 matches. MI captaincy under scrutiny.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Didn't play a single IPL 2026 game. Calf strain and thumb injury. CSK eliminated. The legend's future remains cricket's biggest question at 44.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'Success isn't a given. AI is the most consequential technology of our lifetimes.' Meta cuts 8,000 jobs amid biggest AI push in company history.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Jensen Huang",
            "handle": "nvidia",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Nvidia Q1 revenue hits $82 BILLION — 10x from three years ago. Vera CPU opens 'brand new $200 billion' market. Calls stock stagnation 'one of the mysteries of the universe.'",
            "url": "https://www.instagram.com/nvidia/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "D Gukesh",
            "handle": "gaborisukeshd",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces criticism from Nepomniachtchi: 'Every top Grandmaster would have a good chance against him.' Post-Candidates form under scrutiny.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi visits Italy for talks with Meloni and Cyprus President. 'Melody' candy gift goes viral. India to host Quad Foreign Ministers meet on May 26.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Travis Head",
            "handle": "travishead34",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram story after Virat Kohli handshake controversy goes viral! The SRH vs RCB clash continues to generate debate across the cricket world.",
            "url": "https://www.instagram.com/travishead34/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President backs 'Small AI' for farmers at ATX Singapore 2026. Crisis toolkit gives countries access to $60-100 billion. Indian-American leading global development.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Sunny Deol",
            "handle": "iamsunnydeol",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Lahore 1947 releasing globally August 13, 2026. Directed by Rajkumar Santoshi, produced by Aamir Khan. Reuniting after three decades!",
            "url": "https://www.instagram.com/iamsunnydeol/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Posts AI video of Colbert in dumpster. Defends $1.8B anti-weaponization fund. Skips Don Jr.'s Bahamas wedding: 'love for the United States.'",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX IPO filing at $1.25 trillion valuation. Nvidia concedes China chip market to Huawei. Still posting 25-35 times daily on X.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Met Nvidia CEO Jensen Huang at AI Summit. Reliance expanding into power and telecom. Battles Adani for Asia's richest spot.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Overtakes Mukesh Ambani as Asia's richest man. Adani Group and Reliance collaborating in fuel retail. Building India's infrastructure empire.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Bollywood's most bankable star continues with multiple projects in the pipeline and growing international profile.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-21"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Stree franchise dominance continues. India's social media queen remains the most-followed Indian actress on Instagram.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-21"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM announces free summer bus travel for kids. Congratulates Arsenal on PL title. Co-chairs Hormuz Strait meeting with Macron.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-22"
        },
    ]

    data["posts"] = celeb_updates
    data["last_updated"] = datetime.now(timezone.utc).isoformat()

    with open(CELEB_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Updated {len(celeb_updates)} celebrity posts in celebrity-buzz.json")


if __name__ == "__main__":
    update_tech_buzz()
    update_celebrity_buzz()
