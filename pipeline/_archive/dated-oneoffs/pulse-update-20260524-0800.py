#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-24 08:00 PDT"""

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
            "text": "SpaceX IPO looms at a staggering $1.25-2.2 trillion valuation — potentially the world's largest ever. Tesla stock surges on renewed EV optimism. Musk's empire spans rockets, EVs, AI, and social media as he cements himself as the world's first trillionaire candidate.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-24",
        },
        "zuck": {
            "text": "Meta's massive AI pivot: 8,000 jobs cut, 7,000 reassigned to AI teams. Leaked audio shows Zuckerberg defending employee monitoring to 'win the AI race.' Threads crosses 150M daily active users. No more company-wide layoffs in 2026 — for now.",
            "url": "https://x.com/zuck",
            "date": "2026-05-24",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI hard across Search, Workspace, and Cloud to challenge ChatGPT's dominance. Antitrust concerns mount over AI-energy consumption and market concentration. Regulatory spotlight intensifies as Google integrates AI into virtually every product.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-24",
        },
        "satyanadella": {
            "text": "Microsoft doubles down on AI infrastructure — $80 billion invested, with $30 billion more planned next quarter. Azure surpasses $75 billion in quarterly revenue. Microsoft and OpenAI plan a $100 billion AI supercomputer. Copilot enterprise adoption hits record highs.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-24",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 will be 'smarter than the smartest person' as the Musk v. OpenAI lawsuit over the $97.4 billion bid heads toward trial. OpenAI's valuation soars amid intense competition with Meta, Google, and Anthropic. Former employees warn of AI safety risks in new exposé.",
            "url": "https://x.com/sama",
            "date": "2026-05-24",
        },
        "tim_cook": {
            "text": "Apple names John Ternus as Tim Cook's eventual successor — 'the mind of an engineer, the soul of an innovator.' Apple asks Supreme Court to review App Store contempt ruling. WWDC 2026 set to showcase deeper AI integration across iOS and macOS.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-24",
        },
        "nvidia": {
            "text": "Nvidia reports jaw-dropping $81.6 billion Q1 revenue — 10x from three years ago. Unveils Vera Rubin platform delivering 10x inference throughput per megawatt over Blackwell. CEO Jensen Huang sees $1 trillion in orders through next year. Concedes China AI chip market to Huawei amid US export controls.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-24",
        },
        "NandanNilekani": {
            "text": "Infosys co-founder's Fundamentum Partnership backs India's digital infra startups as Big Tech pours $50 billion into India for AI, cloud, and digital infrastructure. India emerging as global AI talent hub. US tariff policies could impact IT services giants Infosys and TCS.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-24",
        },
        "BillGates": {
            "text": "Bill Gates criticizes calls for AI development pauses, argues stopping progress is counterproductive. Continues pushing global health initiatives through the Gates Foundation. Warns that AI's benefits in healthcare and education far outweigh the risks of slowing down.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-24",
        },
        "ArvindKrishna": {
            "text": "IBM CEO expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise adoption of trustworthy Generative AI using watsonx platform, targeting hybrid and on-premises environments. IBM positions itself as the 'safe enterprise AI' choice.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-24",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO integrates generative AI across Creative Cloud and Experience Cloud. Firefly family of models gains traction against Midjourney and DALL-E. Adobe bets its future on being the AI-powered creative platform of choice for enterprises.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-24",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal maintains low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley's startup ecosystem.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair continues leading the luxury brand's digital and sustainability transformation. The Indian-origin executive remains one of the highest-profile diaspora leaders in global fashion and luxury.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-24",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates global supply chain shifts as US-Iran tensions roil shipping routes through the Strait of Hormuz. FedEx adapts logistics as trade policy uncertainty under the Big Beautiful Bill impacts corporate planning.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-24",
        },

        # === WORLD / POWER PULSE (16) ===
        "realDonaldTrump": {
            "text": "Trump announces Iran deal 'largely negotiated' — Strait of Hormuz to reopen. Iran agrees to surrender enriched uranium, commit to never pursuing nuclear weapons. 60-day ceasefire extension proposed. Separately, administration orders green card applicants to leave the US during processing — a sweeping policy shift affecting hundreds of thousands of legal visa holders. Tulsi Gabbard resigns as DNI, citing husband's cancer diagnosis.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-24",
        },
        "WhiteHouse": {
            "text": "White House blasts Cruz, Pompeo for 'undermining' Iran peace efforts. Trump stays in DC while Don Jr. weds Bettina Anderson. New green card policy forces applicants abroad — USCIS calls adjustment of status 'extraordinary relief.' Executive order allows 401(k) crypto investment. Big Beautiful Bill advances with expanded SALT deductions.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-24",
        },
        "Keir_Starmer": {
            "text": "UK PM co-chairs 40+ nation Paris meeting with Macron on keeping Strait of Hormuz open. Announces free summer bus travel for kids across England. Defends EU alignment plans as Reform UK's Farage surges in polls with aggressive anti-immigration platform.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-24",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosts Paris summit with Starmer on Strait of Hormuz freedom of navigation as US-Iran deal nears finalization. France positions itself as key mediator in Middle East peace efforts. Domestic pressure mounts from right-wing parties.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-24",
        },
        "AlboMP": {
            "text": "Australian PM Albanese monitors Strait of Hormuz developments closely as global shipping disruptions threaten energy imports. Australia navigates delicate balance between US alliance commitments and regional trade interests in the Indo-Pacific.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-24",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy slams racism within conservative circles, saying those who call Usha Vance a 'jeet' have 'no place' in the movement. The Indian-American entrepreneur continues positioning himself as a unifying voice in the MAGA coalition.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-24",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak watches from the sidelines as Reform UK's anti-immigration platform reshapes British politics. The Conservative Party struggles to find direction post-Sunak, with Reform surging in polls and proposing radical migrant detention policies.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-24",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance thrust into spotlight as Vivek Ramaswamy defends her against racist slurs from within conservative circles. The Indian-American attorney and wife of VP JD Vance navigates the complexities of being a diaspora figure in MAGA world.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-24",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel continues reshaping the bureau as Tulsi Gabbard announces departure from DNI role. The Trump administration's intelligence and law enforcement apparatus undergoes major personnel shifts heading into summer.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-24",
        },
        "SriramKrishnan": {
            "text": "White House AI policy advisor Sriram Krishnan shapes Trump's AI executive orders, including new contractor oversight rules and a tech advisory council. The Indian-American venture capitalist brings Silicon Valley thinking to federal AI governance.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-24",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman navigates a fractured Conservative landscape as Reform UK's hardline immigration stance steals the party's thunder. The Indian-origin Tory continues to push for tougher border controls.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-24",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga shapes global development policy as the US-Iran deal could reshape Middle East economics. Indian-American diaspora leaders increasingly influential in international economic governance. Banga pushes climate finance and digital infrastructure for developing nations.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-24",
        },
        "HHShkMohd": {
            "text": "Dubai ruler Mohammed bin Rashid watches closely as the US-Iran deal could reopen the Strait of Hormuz. UAE's strategic position as a regional trade and logistics hub depends on stability in the Persian Gulf. Gulf nations push for permanent resolution.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-24",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Giorgia Meloni deepens strategic partnership with Modi after his Italy visit. PM Modi's gift of a Parle 'Melody' chocolate to Meloni sends Parle Industries stock surging. Italy-India ties strengthen across defense, tech, and cultural exchanges.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-24",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Christopher Luxon navigates global trade tensions as US tariff policies create uncertainty for Pacific exporters. NZ monitors Strait of Hormuz developments and their potential impact on energy costs and shipping routes.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-24",
        },

        # === INDIA PULSE (12) ===
        "narendramodi": {
            "text": "PM Modi chairs high-level security meeting with Amit Shah, Jaishankar, NSA Ajit Doval, and CDS Anil Chauhan on the escalating US-Iran-Israel conflict. Distributes 51,000 government appointment letters. Strengthens Italy ties — Parle stock surges after Modi gifts 'Melody' to Meloni. BJP sweeps West Bengal with 207 seats in historic first right-wing victory.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-24",
        },
        "PMOIndia": {
            "text": "PMO convenes emergency national security review as US-Iran war tensions escalate. Modi's 'Viksit Bharat 2047' vision highlighted at council meeting. Government pushes massive recruitment drive with 51,000 appointment letters distributed nationwide.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-24",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah attends PM Modi's high-level security meeting on the US-Iran-Israel conflict alongside Jaishankar and NSA Doval. BJP celebrates historic West Bengal victory — 207 seats, ending decades of left and TMC dominance in the state.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-24",
        },
        "RahulGandhi": {
            "text": "Rahul Gandhi warns of a major economic crisis, blames Modi's policies for favoring Adani and Ambani while ordinary citizens face severe hardship. Criticizes government's focus on foreign tours over economic stability. Congress urges states to prepare for potential slowdowns.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-24",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath lauds BJP's historic West Bengal victory as vindication of Hindutva politics. Fuel prices in BJP-ruled states remain lower than Congress-led states, the party claims. Yogi continues positioning himself as a national BJP powerhouse.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-24",
        },
        "ArvindKejriwal": {
            "text": "AAP chief Arvind Kejriwal navigates post-election positioning as BJP's West Bengal sweep reshapes national politics. AAP continues to consolidate its base in Delhi and Punjab while BJP's pan-India dominance grows.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-24",
        },
        "DrSJaishankar": {
            "text": "External Affairs Minister S. Jaishankar attends PM Modi's emergency security meeting on the US-Iran-Israel conflict. India carefully balances ties with both the US and Iran as the Strait of Hormuz crisis threatens India's oil imports and shipping routes.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-24",
        },
        "nsitharaman": {
            "text": "Finance Minister Nirmala Sitharaman monitors economic fallout from the Iran-US conflict as global oil prices and shipping routes face disruption. India's fiscal strategy under pressure as Rahul Gandhi warns of economic crisis ahead.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-24",
        },
        "rashtrapatibhvn": {
            "text": "Rashtrapati Bhavan watches as India navigates a complex geopolitical moment — the US-Iran deal, West Bengal election results, and strengthening ties with Italy and the Gulf nations. India's democratic institutions face a pivotal period.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-24",
        },
        "gautam_adani": {
            "text": "Adani Group expands into green energy, ports, and data centers as $50B Big Tech investment wave hits India. Faces renewed political attacks from Rahul Gandhi over Modi-Adani ties. Infrastructure empire keeps growing across power, logistics, and clean energy.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-24",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands aggressively into power and telecom after scrapping family noncompete agreement with brother Anil. $1B+ investments in telecom infrastructure and clean energy. Shares rise 4.9% on the announcement. Strategic push into data centers as India's AI demand explodes.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-24",
        },
        "RNTata2000": {
            "text": "Ratan Tata Foundation continues legacy projects as US tariff policies create uncertainty for Indian IT services firms TCS and Infosys. The Tata Group navigates geopolitical crosswinds while expanding its global footprint in steel, auto, and technology.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-24",
        },

        # === SPORTS PULSE (15) ===
        "imVkohli": {
            "text": "Virat Kohli's IPL 2026 campaign includes his 9th IPL hundred and the milestone of 14,000 T20 runs — the first Indian batter to reach the mark. RCB finish top of the table with 18 points and head into Qualifier 1 against Gujarat Titans.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-24",
        },
        "ImRo45": {
            "text": "Rohit Sharma's MI finish 9th in IPL 2026 — a disappointing campaign ending with a 30-run loss to Rajasthan Royals at Wankhede. MI managed just 175/9 chasing RR's 205/8. A season to forget for the five-time champions.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-24",
        },
        "msdhoni": {
            "text": "Captain Cool watches from the sidelines as IPL 2026 enters its dramatic final day. Top 3 sealed — RCB, GT, SRH all on 18 points. Three teams fight for the 4th playoff spot. Arjun Tendulkar plays for LSG as next-gen cricketers carry forward legends' legacy.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-24",
        },
        "Jaspritbumrah93": {
            "text": "Jasprit Bumrah delivers another masterclass — takes key wickets as MI vs RR battle plays out at Wankhede. Despite MI's 9th-place finish, Bumrah remains India's premier fast bowler. All eyes on him for the upcoming international season.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-24",
        },
        "hardikpandya7": {
            "text": "Hardik Pandya scores 34 in MI's losing cause against RR at Wankhede. MI's IPL 2026 ends in 9th place after a 30-run defeat. Pandya's all-round abilities couldn't rescue a misfiring squad in what will be a painful campaign review.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-24",
        },
        "BCCI": {
            "text": "IPL 2026 final day delivers high drama. Top 3 confirmed: RCB #1, GT #2, SRH #3 — all on 18 points separated by NRR. Rajasthan Royals beat MI by 30 runs to book the 4th playoff spot. PBKS, KKR eliminated despite late surge. Playoff final at Ahmedabad's Narendra Modi Stadium.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-24",
        },
        "ICC": {
            "text": "ICC watches as IPL 2026 delivers one of the most dramatic playoff races in tournament history. Three teams on 18 points, three more fighting for the final spot on the last day. The T20 format continues to captivate global audiences.",
            "url": "https://x.com/ICC",
            "date": "2026-05-24",
        },
        "IPL": {
            "text": "IPL 2026 final league day: RR beat MI by 30 runs at Wankhede to seal the 4th playoff spot. RCB vs GT in Qualifier 1. SRH in Eliminator. Shreyas Iyer's century for PBKS was heroic but ultimately in vain. Vaibhav Sooryavanshi's 53 sixes this season just one short of the all-time record. The final heads to Ahmedabad.",
            "url": "https://x.com/IPL",
            "date": "2026-05-24",
        },
        "Neeraj_chopra1": {
            "text": "Olympic champion Neeraj Chopra continues Diamond League campaign as India's top athletics hope. The javelin star trains for the 2026 season with eyes on defending his world-class form ahead of major international competitions.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-24",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu continues her badminton comeback, targeting international tournaments in the 2026 season. The double Olympic medalist balances competitive ambitions with growing brand endorsements and mentoring the next generation of Indian shuttlers.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Tennis icon Sania Mirza continues her post-retirement journey, focusing on mentoring young Indian tennis talent and brand ambassadorship. The six-time Grand Slam champion remains India's most celebrated tennis star.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces heat from Russian GM Nepomniachtchi: 'Every top GM would have a good chance against him.' The youngest-ever world champion takes a classical break to prepare for his title defense against Candidates winner Sindarov later this year.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-24",
        },
        "chetrisunil11": {
            "text": "India football legend Sunil Chhetri's legacy continues to inspire as AIFF announces 2026-27 Club Licensing results. Indian football development programs expand with new coaching initiatives and infrastructure investment.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-24",
        },
        "sachin_rt": {
            "text": "Sachin Tendulkar watches son Arjun play for Lucknow Super Giants in IPL 2026. LSG fall short as Punjab Kings chase down 196/6 — Shreyas Iyer's maiden IPL century seals the win. Cricket's greatest legacy extends to the next generation on the biggest stage.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-24",
        },
        "SGanguly99": {
            "text": "Former BCCI president Sourav Ganguly watches IPL 2026's dramatic finale from the commentary box. KKR face DC in a do-or-die clash at Eden Gardens — Ganguly's home turf. The tournament's playoff race goes down to the final day.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-24",
        },
    }

    for handle, upd in updates.items():
        if handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            leader["text"] = upd["text"]
            leader["url"] = upd["url"]
            leader["date"] = upd["date"]
            updated += 1

    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(TECH_BUZZ, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"✅ tech-buzz.json: {updated} leaders updated")


def update_celebrity_buzz():
    celeb_posts = [
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Trump declares Iran deal 'largely negotiated' — Strait of Hormuz to reopen, Iran to surrender enriched uranium. 60-day ceasefire extension proposed. Separately orders green card applicants to leave US during processing — hundreds of thousands of legal visa holders impacted. Don Jr. weds Bettina Anderson as Trump stays in DC.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "King Kohli's IPL 2026: 9th IPL hundred, first Indian to 14,000 T20 runs. RCB finish #1 with 18 points and head to Qualifier 1. The run machine's hunger for trophies remains insatiable as RCB chase their maiden IPL title.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi chairs emergency security meeting with Shah, Jaishankar, Doval on US-Iran-Israel conflict. BJP sweeps West Bengal with 207 seats — historic first right-wing victory in the state. 51,000 appointment letters distributed. Parle stock surges after Modi gifts 'Melody' to Italian PM Meloni.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Captain's knock of a lifetime — Shreyas Iyer smashes maiden IPL century (101* off 51 balls) to keep PBKS' playoff dreams alive. Punjab end six-match losing streak, beat LSG by 7 wickets. Three teams, one spot, final day drama — IPL 2026 at its absolute best.",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborofficial",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Aishwarya Rai stuns at Cannes 2026 closing ceremony in a pearlescent white power pantsuit with dramatic faux feathers. Daughter Aaradhya joins her on the red carpet in a matching pastel pink ensemble. L'Oréal Paris ambassador continues to own the French Riviera.",
            "url": "https://www.instagram.com/aaborofficial/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX files for what could be the world's largest IPO at $1.25-2.2 trillion valuation. Tesla surges on renewed EV optimism. The world's richest man keeps pushing boundaries across space, AI, and electric vehicles while SpaceX's Starship program accelerates.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 8,000 jobs cut, 7,000 reassigned to AI. Leaked audio shows Zuck defending employee monitoring for the AI race. 'Success isn't a given.' Threads crosses 150M daily active users. The billionaire bets everything on winning the AI wars.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' — Shah Rukh Khan's ₹350 crore action thriller with daughter Suhana and Deepika Padukone — may release September 2026, moved up from Christmas. Reports suggest the film could split into two parts. Bollywood's biggest franchise bet of the year.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Captain Cool watches from the sidelines as IPL 2026's dramatic final day unfolds. Top 3 sealed: RCB, GT, SRH. Three teams fight for the last playoff spot. The legend's shadow still looms large over T20 cricket even in retirement.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI's IPL 2026 ends in heartbreak — 30-run loss to RR at Wankhede, finish 9th. Hardik scores 34 in a losing cause. A season to forget for the five-time champions. Pandya faces tough questions about MI's misfiring squad ahead of the next auction.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika Padukone and Ranveer Singh return to Mumbai after celebrating her birthday in New York. Stars alongside SRK and Suhana in 'King' — the ₹350 crore action thriller that could move to a September 2026 release. Christmas box office war heats up with Avengers and Dune 3.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit Dosanjh's North American concert tour continues to sell out city after city. The Punjabi superstar has become the face of Indian music going global, bridging Bollywood and the diaspora like no one before.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer Singh's post-apocalyptic thriller 'Pralay' begins filming August 2026 with a massive ₹300 crore budget. Returns from New York after celebrating Deepika's birthday. Meanwhile Vicky Kaushal blocks 18 months for 'Mahavatar' — Bollywood bets big on ambitious storytelling.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "The Master Blaster watches son Arjun play for LSG in IPL 2026. LSG fall to PBKS as Shreyas Iyer smashes a maiden IPL century. Cricket's greatest legacy extends to the next generation. Ranbir Kapoor's 'Ramayana' reportedly moves to October 30, 2026 — a week before Diwali.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat from Nepomniachtchi: 'Every top GM would have a good chance against him.' The youngest-ever world champion takes a classical break to prepare for his title defense against Candidates winner Sindarov later this year.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands aggressively into power and telecom after scrapping family noncompete with brother Anil. $1B+ investments, shares up 4.9%. Strategic push into data centers and clean energy as India's AI infrastructure demand explodes.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra continues her Hollywood-Bollywood dual career. Cannes 2026 brings Indian cinema into the global spotlight. 'Jee Le Zaraa' with Alia and Katrina remains one of the most anticipated films. The ultimate NRI success story keeps winning.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's multi-city US tour continues to draw massive diaspora crowds. The playback queen bridges generations of Bollywood music lovers. Upcoming shows in major US cities sell out as Indian live music goes mainstream in America.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress takes a mountain retreat break between projects. Shraddha Kapoor continues to dominate social media with her relatable content style. Bollywood's digital queen reigns supreme.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia Bhatt's 2026 slate includes multiple high-profile projects as she cements her position as Bollywood's most bankable actress. 'Jee Le Zaraa' with Priyanka and Katrina remains the most anticipated girl-trip film. Ranbir's 'Ramayana' eyes October release.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, and data centers as $50B Big Tech investment wave hits India. Faces Rahul Gandhi's renewed political attacks over Modi-Adani ties. The infrastructure empire keeps growing despite controversy.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chairs 40+ nation Paris summit with Macron on Strait of Hormuz freedom of navigation. Free summer bus travel for kids. Reform UK's aggressive anti-immigration platform puts pressure on Starmer's Labour government.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga shapes global development policy as US-Iran deal could reshape Middle East economics. The Indian-American diaspora leader pushes climate finance and digital infrastructure for developing nations.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-24"
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
    print("✅ All pulse data updated for 2026-05-24 08:00 PDT")
