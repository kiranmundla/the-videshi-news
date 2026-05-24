#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-24 11:00 PDT"""

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
            "text": "SpaceX IPO filing at $1.25-2.2 trillion valuation dominates markets — potentially the world's largest-ever listing. SpaceX Starlink launch scheduled Monday (Memorial Day) from Cape Canaveral. Tesla stock surges on renewed EV optimism. Analysts warn SpaceX IPO could divert investor focus from Tesla. SpaceX and Tesla still hold 18,486 bitcoins with $1.7B in profits.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-24",
        },
        "zuck": {
            "text": "Meta's massive AI pivot continues: 8,000 jobs cut, 7,000 reassigned to AI teams. Leaked audio shows Zuckerberg defending employee monitoring to 'win the AI race.' Threads crosses 150M daily active users. Trump scuttled federal AI oversight executive order after lobbying from Musk, Zuckerberg, and AI czar David Sacks.",
            "url": "https://x.com/zuck",
            "date": "2026-05-24",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI hard across Search, Workspace, and Cloud. Jensen Huang says Anthropic and OpenAI are 'about to go public' — intensifying the AI competition with Google. Antitrust concerns mount over AI-energy consumption and market concentration as regulators sharpen focus on Big Tech.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-24",
        },
        "satyanadella": {
            "text": "Microsoft doubles down on AI infrastructure — $80 billion invested, with $30 billion more planned. Azure surpasses $75 billion in quarterly revenue. Microsoft and OpenAI plan a $100 billion AI supercomputer. Copilot enterprise adoption hits record highs. OpenAI IPO looming could reshape the partnership.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-24",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 will be 'smarter than the smartest person' as the Musk v. OpenAI lawsuit over the $97.4 billion bid heads toward trial. Jensen Huang confirms OpenAI is 'about to go public.' OpenAI's valuation soars amid intense competition. Former employees warn of AI safety risks in new exposé.",
            "url": "https://x.com/sama",
            "date": "2026-05-24",
        },
        "tim_cook": {
            "text": "Apple names John Ternus as Tim Cook's eventual successor — 'the mind of an engineer, the soul of an innovator.' Apple asks Supreme Court to review App Store contempt ruling. WWDC 2026 set to showcase deeper AI integration across iOS and macOS. Apple's AI strategy under scrutiny as rivals accelerate.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-24",
        },
        "nvidia": {
            "text": "Nvidia CEO Jensen Huang says $200 billion CPU market forecast includes China despite US export controls — signals long-term demand. Reports jaw-dropping $81.6 billion Q1 revenue (10x from three years ago). Confirms Anthropic and OpenAI are 'about to go public.' Memory suppliers expected to boost HBM capacity swiftly for Vera Rubin platform.",
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
            "text": "IBM CEO expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise adoption of trustworthy Generative AI using watsonx platform, targeting hybrid and on-premises environments. IBM positions itself as the 'safe enterprise AI' choice amid the OpenAI/Anthropic IPO wave.",
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
            "text": "FedEx CEO Raj Subramaniam navigates global supply chain shifts as US-Iran tensions roil shipping routes through the Strait of Hormuz. Trump says 'no rush' on Iran deal — Hormuz reopening still uncertain. FedEx adapts logistics as trade policy uncertainty under the Big Beautiful Bill impacts corporate planning.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-24",
        },

        # === WORLD / POWER PULSE (15) ===
        "realDonaldTrump": {
            "text": "Trump walks back urgency on Iran deal — says 'no rush' and 'time is on our side.' Senior official confirms deal won't be signed Sunday despite Saturday's 'largely negotiated' claim. White House shooting: Nasire Best (21, Maryland) killed by Secret Service — third WH incident in a month; bystander in critical condition. Trump renews call for White House ballroom for security. Tulsi Gabbard resigns as DNI.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-24",
        },
        "WhiteHouse": {
            "text": "White House says Iran deal 'far from finished' after Trump's 'no rush' reversal. Nasire Best (21), who 'believed he was Jesus Christ,' had mental health history and prior Secret Service arrest — third security incident in a month. Bystander remains in critical condition. Big Beautiful Bill advances with 39.6% millionaire tax bracket and expanded SALT deductions. Executive order allows 401(k) crypto investment.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-24",
        },
        "Keir_Starmer": {
            "text": "UK PM co-chairs 40+ nation Paris summit with Macron on Strait of Hormuz freedom of navigation. Trump's 'no rush' on Iran deal complicates diplomatic momentum. Free summer bus travel for kids. Reform UK's aggressive anti-immigration platform puts pressure on Starmer's Labour government.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-24",
        },
        "AlboMP": {
            "text": "Australian PM Albanese monitors Hormuz crisis impact on energy prices and regional stability. Australia's Quad commitment strengthened ahead of May 26 Foreign Ministers' Meeting in New Delhi. Climate and Pacific Island diplomacy remain key priorities.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-24",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Luxon navigates rising global trade tensions and Pacific Island diplomacy. NZ economy shows mixed signals as commodity prices fluctuate with Hormuz uncertainty.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-24",
        },
        "HHShkMohd": {
            "text": "Dubai ruler Sheikh Mohammed bin Rashid monitors the proposed US-Iran deal closely — Strait of Hormuz reopening would directly benefit UAE trade and shipping. UAE was among the countries Trump consulted on Saturday's multi-leader call. Dubai continues aggressive economic diversification.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-24",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Giorgia Meloni strengthens bilateral ties after PM Modi gifted 'Melody' chocolates at recent meeting — Parle stock surged. Italy aligns with EU on Hormuz freedom of navigation stance at Paris summit. Cannes Film Festival wraps — Mungiu's Fjord wins Palme d'Or.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-24",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosts 40+ nation Paris summit on Strait of Hormuz freedom of navigation with Starmer. France pushes multilateral approach as Trump says 'no rush' on Iran deal. Cannes 2026 wraps — Mungiu's Fjord wins Palme d'Or; Neon's 7th consecutive win. Barbra Streisand honored with honorary Palme.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-24",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy continues advising on Trump's deregulation agenda after DOGE stint. Iran deal negotiations and the Big Beautiful Bill's tax provisions draw attention. The Indian-American political figure remains influential in GOP policy circles.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-24",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak navigates post-leadership political positioning as Starmer's Labour government co-chairs Hormuz summit. The first British-Indian PM continues to represent diaspora achievement on the global stage. Reform UK's rise challenges both Labour and the Tory establishment.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-24",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance maintains public presence amid the Trump administration's Iran peace push and Big Beautiful Bill negotiations. The Indian-American Yale Law graduate represents a new generation of diaspora political influence in Washington.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-24",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel faces security spotlight after third White House shooting incident in a month — Nasire Best (21) killed by Secret Service after opening fire at checkpoint. The Indian-American FBI chief oversees heightened domestic threat assessment.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-24",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan navigates the aftermath of Trump scrapping the federal AI oversight executive order — lobbied against by Musk, Zuckerberg, and AI czar David Sacks. The Indian-American tech advisor shapes the administration's pro-innovation AI stance.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-24",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman continues pushing hardline immigration stance. The Indian-origin Tory leadership contender faces a shifting political landscape as Reform UK surges on anti-immigration platform, pressuring both Labour and Conservatives.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-24",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga monitors how the US-Iran deal could reshape Middle East economics and global energy markets. Trump's 'no rush' stance prolongs uncertainty. The Indian-American diaspora leader pushes climate finance and digital infrastructure for developing nations.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-24",
        },

        # === INDIA PULSE (12) ===
        "narendramodi": {
            "text": "PM Modi hosts US Secretary of State Marco Rubio — extends White House invitation, announces 'Mission 500' targeting $500B bilateral trade by 2030. BJP sweeps West Bengal with 207 seats — historic first right-wing victory in the state. Rubio calls India-US partnership 'among the world's most important.' Quad Foreign Ministers' Meeting set for May 26 in New Delhi.",
            "url": "https://x.com/naaborendramodi",
            "date": "2026-05-24",
        },
        "PMOIndia": {
            "text": "PM Modi chairs emergency security meeting on US-Iran conflict with Shah, Jaishankar, and Doval. Hosts Rubio at Hyderabad House — 'Mission 500' $500B trade target by 2030 announced. BJP's Bengal sweep with 207 seats validates Modi's national expansion strategy. 51,000 appointment letters distributed.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-24",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah attends emergency security meeting on Iran crisis. BJP's West Bengal sweep (207 seats) marks the culmination of Shah's long-term strategy to penetrate the eastern bastion. The Bengal win is the biggest BJP breakthrough since Gujarat.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-24",
        },
        "RahulGandhi": {
            "text": "Rahul Gandhi's Congress faces catastrophic West Bengal results — AITC loses 80 seats to BJP's 207-seat sweep. Renews attacks on Modi-Adani ties as $50B Big Tech investment wave reaches India. Congress struggles to find a narrative against BJP's national dominance.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-24",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath celebrates BJP's West Bengal breakthrough — 207 seats in a state that rejected right-wing politics for decades. UP's governance model touted as blueprint for Bengal transformation. Viksit Bharat 2047 agenda remains the guiding framework.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-24",
        },
        "ArvindKejriwal": {
            "text": "AAP chief Arvind Kejriwal watches BJP's Bengal sweep with concern for opposition unity. The 207-seat mandate complicates INDIA alliance strategy for 2029. AAP's own Delhi position remains tenuous as BJP expands nationally.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-24",
        },
        "DrSJaishankar": {
            "text": "EAM Jaishankar holds delegation-level talks with US Secretary of State Rubio at Hyderabad House — outlines 5-point approach: dialogue, uninterrupted maritime trade, opposition to weaponizing trade, energy security, and nuclear partnerships. Quad Foreign Ministers' Meeting May 26 in Delhi. Rubio calls partnership 'comprehensive global strategic.'",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-24",
        },
        "nsitharaman": {
            "text": "Finance Minister Nirmala Sitharaman monitors Iran deal impact on oil prices and India's import bill. Hormuz uncertainty could drive crude higher. Big Tech's $50B India investment wave and 'Mission 500' trade target with the US reshape economic outlook.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-24",
        },
        "rashtrapatibhvn": {
            "text": "President Droupadi Murmu oversees the aftermath of West Bengal's historic election — BJP's 207 seats represent the first right-wing government in the state's history. New government formation expected soon. Constitutional role steady amid national political realignment.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-24",
        },
        "gautam_adani": {
            "text": "Adani Group pushes into green energy, ports, and data centers as $50B Big Tech investment wave hits India. Faces Rahul Gandhi's renewed political attacks over Modi-Adani ties. AdaniConneX expanding India data center footprint aggressively as AI demand explodes.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-24",
        },
        "RelianceJio": {
            "text": "Reliance expands aggressively into power and telecom after scrapping family noncompete with brother Anil. $1B+ investments, shares up 4.9%. Strategic push into data centers and clean energy as India's AI infrastructure demand explodes. Mission 500 trade target could unlock new US partnerships.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-24",
        },
        "RNTata2000": {
            "text": "Ratan Tata Foundation continues driving philanthropic impact across education, healthcare, and innovation. Tata Group's semiconductor fab plans in Gujarat position India as a chip manufacturing hub. The Tata legacy grows amid India's $50B tech investment wave.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-24",
        },

        # === SPORTS PULSE (15) ===
        "imVkohli": {
            "text": "Kohli's RCB finished #1 with 18 points — head to Qualifier 1 as the top seed. King Kohli's IPL 2026: 9th IPL hundred, first Indian to 14,000 T20 runs. Meanwhile RR beat MI by 30 runs and DC beat KKR by 40 runs in today's double-header, completing the league stage picture.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-24",
        },
        "ImRo45": {
            "text": "Rohit Sharma's MI fall to Rajasthan Royals by 30 runs at Wankhede — MI bowled out for 175 chasing 206. Season ends for Mumbai Indians. Yuzvendra Chahal had joked 'Hope RR lose and Rohit scores 200' — neither happened. Hitman's IPL 2026 campaign ends on a low note.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-24",
        },
        "msdhoni": {
            "text": "MS Dhoni watches the IPL playoffs picture emerge — RR secure their spot with a 30-run win over MI, DC cruise past KKR by 40 runs. Thala's CSK await their playoff fate. The IPL legend continues to draw massive fan engagement even from the dugout.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-24",
        },
        "Jaspritbumrah93": {
            "text": "Jasprit Bumrah's MI season ends with a 30-run loss to Rajasthan Royals at Wankhede. MI could only manage 175/9 chasing 206. The world's best fast bowler faces an early off-season. India's ICC Champions Trophy and T20 World Cup preparations beckon.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-24",
        },
        "hardikpandya7": {
            "text": "Captain Hardik Pandya's MI fall to RR by 30 runs at Wankhede — MI bowled out for 175 chasing 206. A disappointing end to MI's IPL 2026 campaign. Pandya's captaincy record under scrutiny as Mumbai Indians exit early again.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-24",
        },
        "BCCI": {
            "text": "IPL 2026 league stage nears completion — today's double-header: RR beat MI by 30 runs at Wankhede (RR 205/8, MI 175/9), DC beat KKR by 40 runs at Eden Gardens (DC 203/5, KKR 163/10). Playoff picture crystalizing. SAFF Women's Championship 2026 starts tomorrow in Goa — India vs Maldives opener.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-24",
        },
        "ICC": {
            "text": "ICC monitors IPL 2026's penultimate weekend — RR and DC win today's double-header. League stage approaching climax with playoffs imminent. SAFF Women's Championship kicks off May 25 in Margao, Goa. Global cricket calendar packed through the summer.",
            "url": "https://x.com/ICC",
            "date": "2026-05-24",
        },
        "IPL": {
            "text": "IPL 2026 Match Day: RR beat MI by 30 runs at Wankhede (Jofra Archer, Jadeja star; RR 205/8 → MI 175/9). DC beat KKR by 40 runs at Eden Gardens (KL Rahul, Axar Patel shine; DC 203/5 → KKR 163/10). RCB finish #1 with 18 points. Playoffs loading — Qualifier 1 and Eliminator up next. Season ends May 31.",
            "url": "https://x.com/IPL",
            "date": "2026-05-24",
        },
        "Neeraj_chopra1": {
            "text": "Olympic gold medalist Neeraj Chopra continues training for the 2026 Diamond League circuit and 2028 LA Olympics preparation. India's greatest track & field athlete remains the face of Indian athletics on the global stage.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-24",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu gears up for the 2026 BWF World Tour circuit as badminton season intensifies. The double Olympic medalist continues to be India's biggest name in badminton and a major brand ambassador globally.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-24",
        },
        "MirzaSania": {
            "text": "Sania Mirza continues her post-retirement media and mentorship career. India's greatest tennis player remains a powerful voice for women in sport and diaspora representation in global athletics.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-24",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces heat from Nepomniachtchi: 'Every top GM would have a good chance against him.' The youngest-ever world champion takes a classical break to prepare for his title defense against Candidates winner Sindarov later this year.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-24",
        },
        "chetrisunil11": {
            "text": "Sunil Chhetri's legacy looms large as SAFF Women's Championship 2026 starts tomorrow in Goa — India vs Maldives opener. ISL governance crisis deepens: 7 of 14 clubs denied licences, AIFF under fire. Indian football at a crossroads with FIFA World Cup 2026 weeks away.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-24",
        },
        "sachin_rt": {
            "text": "Sachin Tendulkar watches son Arjun play for LSG in IPL 2026. Today's IPL double-header: RR beat MI by 30 runs, DC beat KKR by 40 runs — league stage nearing climax. Cricket's greatest legacy extends to the next generation as playoffs approach.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-24",
        },
        "SGanguly99": {
            "text": "Sourav Ganguly's KKR fall to Delhi Capitals by 40 runs at Eden Gardens — KKR bowled out for 163 chasing 204. A tough day for the former India captain's franchise. Bengal's political landscape transforms with BJP's historic 207-seat sweep.",
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
            if "latestPost" in leader:
                leader["latestPost"]["text"] = upd["text"]
                leader["latestPost"]["url"] = upd["url"]
                leader["latestPost"]["date"] = upd["date"]
            updated += 1

    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    data["lastUpdated"] = data["last_updated"]
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
            "caption": "Trump walks back Iran deal urgency — 'no rush' and 'time is on our side.' Senior official confirms deal won't be signed Sunday. White House shooting: Nasire Best (21) killed by Secret Service — third WH incident in a month, bystander critical. Renews call for White House ballroom for security.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "King Kohli's RCB finish #1 with 18 points — headed to Qualifier 1 as top seed. IPL 2026's most dominant campaign: 9th IPL hundred, first Indian to 14,000 T20 runs. Today's results: RR beat MI by 30 runs, DC beat KKR by 40 runs. Playoffs loading.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi hosts Rubio at Hyderabad House — 'Mission 500' $500B trade target by 2030 announced. BJP sweeps West Bengal with 207 seats — historic first right-wing victory. Quad FM Meeting May 26 in Delhi. Jaishankar outlines 5-point diplomatic framework with the US.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreyas Iyer's maiden IPL century (101* off 51 balls) kept PBKS' playoff dreams alive in yesterday's win over LSG. Today RR beat MI by 30 runs and DC beat KKR by 40 runs — playoff picture crystallizing. PBKS await their fate.",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborishwaryaraibachchan_arb",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Aishwarya Rai dominated Cannes 2026 fashion with a striking tuxedo-inspired outfit as the festival awarded Palme d'Or to Mungiu's Fjord. The eternal queen of Cannes red carpets. Deepika uses body double for action in King and Raka due to pregnancy.",
            "url": "https://www.instagram.com/aaborishwaryaraibachchan_arb/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX IPO at $1.25-2.2 trillion could be the world's largest-ever listing. Analysts warn it could divert investor focus from Tesla. Memorial Day Starlink launch Monday from Cape Canaveral. SpaceX and Tesla hold 18,486 bitcoins ($1.7B profits). Jensen Huang says OpenAI and Anthropic 'about to go public.'",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI pivot: 8,000 jobs cut, 7,000 reassigned to AI teams. Leaked audio: Zuck defends employee monitoring to 'win the AI race.' Threads at 150M DAUs. Trump killed federal AI oversight after lobbying from Musk, Zuckerberg, and Sacks.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SRK's 'King' may split into 2 parts (Part 1 September 2026). Deepika Padukone uses body double for action sequences due to pregnancy — both in King and Atlee's Raka. Ranbir's Ramayana reportedly moves to October 30, 2026. Dhurandhar heads to Japan release July 10 (₹1,307 crore).",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "MS Dhoni",
            "handle": "maborshidhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Thala watches the IPL playoff picture emerge — RR beat MI by 30 runs at Wankhede, DC cruise past KKR by 40 runs at Eden Gardens. CSK await their playoff fate. The IPL legend continues to draw massive engagement even from the dugout.",
            "url": "https://www.instagram.com/maborshidhoni/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Captain Hardik's MI fall to RR by 30 runs at Wankhede — bowled out for 175 chasing 206. Disappointing end to MI's IPL 2026 campaign. Pandya's captaincy record under scrutiny as Mumbai exit early again. Focus shifts to India duty.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit Dosanjh plays Madison Square Garden TODAY (May 24-25) — the Aura World Tour's biggest shows. NYC's desi community turns out in force. Tour continues to Toronto, LA, and San Francisco through June 21. The Punjabi superstar continues his global conquest.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer Singh's post-apocalyptic thriller 'Pralay' begins filming August 2026 with a massive ₹300 crore budget. Meanwhile Vicky Kaushal blocks 18 months for 'Mahavatar' — Bollywood bets big on ambitious storytelling.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "The Master Blaster watches son Arjun play for LSG in IPL 2026. Today's double-header: RR beat MI by 30 runs, DC beat KKR by 40 runs — playoffs imminent. Ranbir Kapoor's 'Ramayana' reportedly moves to October 30, 2026.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat from Nepomniachtchi: 'Every top GM would have a good chance against him.' The youngest-ever world champion prepares for his title defense against Candidates winner Sindarov later this year.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete. $1B+ investments, shares up 4.9%. AdaniConneX and Reliance racing to build India's data center backbone as $50B Big Tech investment wave hits. Mission 500: $500B US-India trade by 2030.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra continues her Hollywood-Bollywood dual career. Cannes 2026 wraps with Aishwarya dominating the red carpet. 'Jee Le Zaraa' with Alia and Katrina remains most anticipated. The ultimate NRI success story keeps winning globally.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's multi-city US tour continues to draw massive diaspora crowds. Meanwhile Diljit Dosanjh plays MSG today. Indian live music goes mainstream in America — concerts selling out across major US cities.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress continues to dominate social media. Cannes 2026 wrapped with Aishwarya leading Indian fashion. Bollywood's digital queen takes a break between projects as SRK's King and Ranbir's Ramayana dominate fall release slate.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia Bhatt's 2026 slate includes multiple high-profile projects. 'Jee Le Zaraa' with Priyanka and Katrina remains the most anticipated girl-trip film. Ranbir's 'Ramayana' eyes October 30 release — a week before Diwali. SRK's 'King' may split into 2 parts.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, and data centers. AdaniConneX expanding India data center footprint as AI demand explodes. $50B Big Tech investment wave hits India. Faces Rahul Gandhi's political attacks amid BJP's Bengal sweep.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chairs 40+ nation Paris summit with Macron on Hormuz freedom of navigation. Trump says 'no rush' on Iran deal — complicates diplomatic momentum. Free summer bus travel for kids. Reform UK surges on anti-immigration platform.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga monitors US-Iran deal impact on Middle East economics. Trump's 'no rush' prolongs Hormuz uncertainty. The Indian-American diaspora leader pushes climate finance and digital infrastructure for developing nations. Mission 500 trade target could reshape development flows.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Rohit Sharma",
            "handle": "rohitsharma45",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Rohit Sharma's MI fall to Rajasthan Royals by 30 runs at Wankhede — MI bowled out for 175 chasing 206. Season over for Mumbai Indians. Yuzvendra Chahal's joke — 'Hope RR lose and Rohit scores 200' — neither happened. Hitman's IPL 2026 ends on a low.",
            "url": "https://www.instagram.com/rohitsharma45/",
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
    print("✅ All pulse data updated for 2026-05-24 11:00 PDT")
