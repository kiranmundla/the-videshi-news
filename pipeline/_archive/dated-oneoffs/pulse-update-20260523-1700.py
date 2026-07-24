#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-23 17:00 PDT"""

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
            "text": "SpaceX IPO filing targets $1.25-2.2 trillion valuation — potentially the largest IPO in history. Starship completes 12th test flight from Starbase, Texas. Meanwhile Nvidia CEO Jensen Huang says SpaceX rival in AI has 'largely conceded' China's chip market to Huawei amid US export controls.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-23",
        },
        "zuck": {
            "text": "Meta restructures aggressively: 8,000 jobs cut and 7,000 reassigned to AI teams. Leaked audio reveals Zuckerberg defended employee surveillance to win the AI race. Tells surviving staff: 'I feel the weight of that.' Threads crosses 150M daily active users as Meta's fediverse bet pays off.",
            "url": "https://x.com/zuck",
            "date": "2026-05-23",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI across Search, Workspace, and Cloud to challenge ChatGPT's dominance. Antitrust concerns mount over AI energy consumption and search monopoly. Quad FM meeting in New Delhi on May 26 puts Indo-Pacific tech cooperation in focus — Google's India investments under the spotlight.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-23",
        },
        "satyanadella": {
            "text": "Microsoft defends $80 billion AI infrastructure investment as Azure crosses $75 billion quarterly revenue. Plans $30 billion more in AI infra spending next quarter. Copilot enterprise adoption hits record highs as the AI arms race between Microsoft, Google, and Meta intensifies.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-23",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 — 'smarter than the smartest person' — as Musk v. OpenAI lawsuit over the $97.4B acquisition heads toward trial. OpenAI's valuation soars amid fierce competition. The AI safety debate intensifies as Bill Gates argues development pauses are counterproductive.",
            "url": "https://x.com/sama",
            "date": "2026-05-23",
        },
        "tim_cook": {
            "text": "Apple succession lands on John Ternus — 'the mind of an engineer, the soul of an innovator.' Apple asks Supreme Court to review App Store contempt ruling. Firefly-competitive AI features set for WWDC 2026 as Apple plays catch-up in generative AI.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-23",
        },
        "nvidia": {
            "text": "Nvidia posts jaw-dropping $81.6B Q1 revenue — 10x from three years ago. Stock dips 1.8% despite the record as Dow hits $50,579. Unveils Vera Rubin platform: 10x inference throughput per megawatt over Blackwell. CEO Huang sees $1 trillion in orders through next year but concedes China market to Huawei.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-23",
        },
        "NandanNilekani": {
            "text": "Big Tech pours $50 billion into India for AI, cloud, and digital infrastructure. Infosys co-founder's Fundamentum Partnership continues backing India's digital startups. Quad FM meeting on May 26 will discuss critical tech partnerships as India emerges as a key AI talent hub.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-23",
        },
        "BillGates": {
            "text": "Bill Gates criticizes AI development pauses, argues stopping progress is counterproductive and risks ceding ground to less safety-conscious actors. Continues pushing global health initiatives through the Gates Foundation while maintaining skepticism toward crypto.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-23",
        },
        "ArvindKrishna": {
            "text": "IBM CEO Arvind Krishna expands AI partnerships — Tech Mahindra and IBM to accelerate enterprise adoption of Generative AI using the watsonx platform, targeting hybrid and on-premises environments. India emerging as major enterprise AI deployment hub.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-23",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO continues integrating generative AI across Creative Cloud and Experience Cloud. Firefly family of models gains traction against Midjourney and DALL-E. Competition intensifies in AI creative tools as Meta, Google, and Adobe race to dominate the creator economy.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-23",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal maintains low profile post-Musk acquisition, focusing on AI ventures and advisory roles in Silicon Valley's startup ecosystem. The Indian-American tech diaspora continues to shape global AI leadership.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair continues steering the luxury house through a competitive landscape. The Indian-born executive represents growing diaspora influence in global luxury and fashion leadership. Cannes 2026 puts Chanel back in the spotlight.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-23",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO Raj Subramaniam navigates global logistics amid trade disruptions and shifting supply chains. The Indian-American CEO exemplifies diaspora leadership at the helm of a Fortune 50 company reshaping last-mile delivery with AI.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-23",
        },

        # === INDIA PULSE ===
        "narendramodi": {
            "text": "PM Modi hosts US Secretary of State Marco Rubio in New Delhi — wide-ranging talks on trade, defense, energy, and Indo-Pacific security. Rubio invites Modi to White House. Quad Foreign Ministers' Meeting set for May 26 in Delhi. Modi also distributed 51,000 government appointment letters this week.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-23",
        },
        "PMOIndia": {
            "text": "India-US bilateral ties deepen as Rubio's 4-day India visit sets the stage for Quad FM meeting on May 26. Modi-Rubio talks cover defense cooperation, critical tech, energy security, and West Asia situation. Both sides emphasize 'global good' and free Indo-Pacific.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-23",
        },
        "AmitShah": {
            "text": "Home Minister Amit Shah oversees national security preparations as US Secretary of State Rubio visits India ahead of the Quad FM meeting. Internal security and counter-terrorism cooperation remain key bilateral agenda items.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-23",
        },
        "RahulGandhi": {
            "text": "Congress leader Rahul Gandhi renews attacks on Modi-Adani ties as the Adani Group expands into power, telecom, and green energy. Opposition sharpens its criticism amid $50 billion Big Tech investment wave hitting India.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-23",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi Adityanath continues aggressive infrastructure and development push in India's most populous state. UP positions itself as a key destination for Big Tech's $50B India investment wave in AI and data centers.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-23",
        },
        "ArvindKejriwal": {
            "text": "AAP leader Kejriwal slams what he calls 'dictatorship' in the country, stepping up opposition rhetoric. Delhi politics intensifies as national attention pivots between the Iran deal, Rubio's India visit, and domestic reform debates.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-23",
        },
        "DrSJaishankar": {
            "text": "External Affairs Minister Jaishankar holds strategic talks with US Secretary of State Rubio ahead of the Quad FM Meeting on May 26 in New Delhi. Agenda covers Indo-Pacific, West Asia crisis, defense, energy, and critical tech partnerships. Australia, Japan FMs also meeting Jaishankar and calling on PM Modi.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-23",
        },
        "nsitharaman": {
            "text": "Finance Minister Nirmala Sitharaman monitors India's economic outlook as $50 billion in Big Tech investments pour into India's AI, cloud, and digital infrastructure. Trade and investment talks with the US accelerate during Rubio's India visit.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-23",
        },
        "rashtrapatibhvn": {
            "text": "President Droupadi Murmu presides over the constitutional framework as India hosts critical Quad diplomacy. The nation's global standing strengthens with the US, Japan, and Australia deepening Indo-Pacific cooperation through Delhi.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-23",
        },
        "gautam_adani": {
            "text": "Adani Group pushes aggressively into green energy, ports, and data centers as India attracts $50B in Big Tech investments. Reliance-Adani rivalry intensifies after Ambani scraps family noncompete. Faces renewed political attacks from Rahul Gandhi over Modi-Adani ties.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-23",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands into power and telecom after scrapping the family noncompete with brother Anil. $1 billion telecom infrastructure investment, clean energy push, shares up 4.9%. The Ambani-Adani duopoly reshapes India's corporate landscape.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-23",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its legacy of philanthropy and nation-building. Tata Group companies remain at the forefront as India attracts record foreign investment in AI and digital infrastructure. The Tata ethos of 'giving back' endures.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-22",
        },

        # === WORLD / POWER PULSE ===
        "realDonaldTrump": {
            "text": "Trump declares Iran peace deal 'largely negotiated' — says Strait of Hormuz 'will be opened.' Tells Axios he's '50/50' on deal vs blowing them 'to kingdom come.' MoU being fine-tuned with Pakistan mediating. VP Vance returns to DC. Tulsi Gabbard resigns as DNI — 4th Cabinet departure this term.",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-23",
        },
        "WhiteHouse": {
            "text": "White House navigates Iran deal finalization — 14-point plan with Pakistan mediating. Tulsi Gabbard forced to resign as DNI (citing husband's cancer); Aaron Lukas named acting director. Trump holds calls with Gulf allies and meets with negotiators Witkoff and Kushner. VP Vance returns to DC.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-23",
        },
        "Keir_Starmer": {
            "text": "UK PM Starmer co-chairs 40+ nation Paris meeting with Macron on keeping Strait of Hormuz open. Announces free summer bus travel for kids across England. Defends EU alignment plans as Reform UK's Nigel Farage circles for the kill. The Iran deal's success matters deeply for UK energy security.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-23",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosts 40+ nation Paris summit on Strait of Hormuz security with UK's Starmer. France positions itself at the center of the Iran peace effort. Oil markets and European energy security hang in the balance as the MoU nears finalization.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-23",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad FM meeting in New Delhi on May 26. Indo-Pacific security, technology cooperation, and maritime stability top the agenda as the Iran deal reshapes global energy and security dynamics.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-23",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni's recent Rome meeting with Modi — where a viral 'Melody' candy gift sparked global attention — strengthens Italy-India ties. Europe watches the Iran deal closely as Hormuz reopening would ease energy costs.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-23",
        },
        "HHShkMohd": {
            "text": "UAE ruler Mohammed bin Rashid watches Iran deal developments closely. Gulf nations push for permanent Hormuz resolution. The Gulf's role as trade and logistics hub depends on stable maritime passage — stakes couldn't be higher.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-23",
        },
        "chrisluxonNZ": {
            "text": "New Zealand PM Luxon monitors Indo-Pacific developments as Quad FM meeting approaches May 26. Five Eyes alignment and Pacific security remain NZ's key priorities amid shifting US-Iran and US-China dynamics.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-23",
        },
        "VivekGRamaswamy": {
            "text": "Vivek Ramaswamy continues his post-DOGE political trajectory. Gabbard's forced resignation as DNI makes him the highest-profile Indian-American to have served and departed Trump's inner circle. His 'anti-woke' brand and Ohio political ambitions remain active.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-23",
        },
        "RishiSunak": {
            "text": "Former UK PM Rishi Sunak observes from opposition as Starmer navigates Iran, EU alignment, and Reform UK's rise. Sunak's legacy as Britain's first Indian-origin PM continues to resonate with the global diaspora.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-23",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance — Indian-American Yale Law grad — watches as VP JD Vance returns to DC amid Iran deal finalization. The Vances represent the most prominent Indian-origin family in the current White House inner circle.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-23",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel continues reshaping the Bureau amid Gabbard's departure from DNI. Indian-American influence in national security deepens as the intelligence community transitions to Aaron Lukas as acting DNI. The Iran deal and domestic security remain top priorities.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-23",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan shapes US tech policy as Big Tech pours $50B into India and AI competition intensifies globally. The Indian-American tech executive bridges Silicon Valley and DC at a pivotal moment for AI governance.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-23",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman — Indian-origin Tory — remains vocal on immigration and law enforcement from the backbenches as Starmer's government faces pressure from both Reform UK and the EU alignment debate.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-22",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga shapes global development policy as India hosts the Quad FM meeting and the Iran peace deal takes shape. Indian-American diaspora leaders increasingly drive international economic governance at the highest levels.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-23",
        },

        # === SPORTS PULSE ===
        "imVkohli": {
            "text": "RCB finish top of IPL 2026 table with 18 points despite losing final league match to SRH by 55 runs. Patidar (56) and Krunal Pandya (41*) ensured RCB crossed the 166-run safety mark. Qualifier 1 vs Gujarat Titans on May 26 at Dharamsala. The King awaits his crown.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-23",
        },
        "ImRo45": {
            "text": "Mumbai Indians (4 wins, 9 losses) face Rajasthan Royals at Wankhede tomorrow in the final league match. MI eliminated but playing spoiler — RR need the win for playoff qualification. Rohit's farewell to a forgettable IPL 2026 campaign.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-23",
        },
        "msdhoni": {
            "text": "CSK eliminated from IPL 2026 playoff race. Captain Cool watches from the sidelines as the final day unfolds with RR, PBKS, and KKR battling for the 4th playoff spot. Arjun Tendulkar debuted for LSG this season as the next generation takes center stage.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-23",
        },
        "Jaspritbumrah93": {
            "text": "Bumrah left out of India's T20 World Cup squad — managed carefully for longer formats. IPL 2026's purple cap race features Rabada and Malinga variants. MI's season over but Bumrah's workload management signals bigger plans ahead.",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-23",
        },
        "hardikpandya7": {
            "text": "MI face Rajasthan Royals at Wankhede tomorrow in the final league match. Hardik's all-round abilities tested in a dead rubber that's alive for RR — a win sends Rajasthan through to playoffs. MI's dismal 4-9 season ends with a potential spoiler role.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-23",
        },
        "BCCI": {
            "text": "IPL 2026 enters its final league day: MI vs RR (Wankhede) and KKR vs DC (Eden Gardens) on May 24. Top 3 locked: RCB (1st), GT (2nd), SRH (3rd) — all on 18 points. 4th spot between RR, PBKS, KKR. Playoffs: Qualifier 1 May 26 Dharamsala, Eliminator May 27, Final May 31 Ahmedabad.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-23",
        },
        "ICC": {
            "text": "ICC board meeting in Ahmedabad on May 30 to discuss playing condition changes. IPL 2026 finale week coincides with global cricket governance decisions. T20 World Cup squad selections create ripples — Bumrah, Shubman Gill left out for workload management.",
            "url": "https://x.com/ICC",
            "date": "2026-05-23",
        },
        "IPL": {
            "text": "FINAL DAY: Match 69 MI vs RR at Wankhede, Match 70 KKR vs DC at Eden Gardens — both May 24. Three teams fight for one spot. RR (14 pts) favorites with best NRR. PBKS (13 pts, done playing) pray for RR loss. KKR (13 pts) need to win AND hope. DC eliminated. Playoffs start May 26.",
            "url": "https://x.com/IPL",
            "date": "2026-05-23",
        },
        "Neeraj_chopra1": {
            "text": "India's golden arm Neeraj Chopra preps for the 2026 athletics season. The Federation Cup in Ranchi spotlights India's next wave of track and field talent. Diamond League circuit awaits the Olympic champion's return to the javelin runway.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-23",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu continues her badminton campaign as the international circuit heats up. India's shuttlers look to build momentum through the Super Series events ahead of the Asian Games cycle.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Tennis icon Sania Mirza's legacy continues to inspire Indian tennis. Post-retirement, she remains the most prominent Indian face in global tennis history, mentoring the next generation of players.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh takes a classical break to prepare for his title defense against Candidates winner Sindarov later this year. Russian GM Nepomniachtchi fires: 'Every top GM would have a good chance against him.' The youngest world champion plots his comeback.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-23",
        },
        "chetrisunil11": {
            "text": "AIFF announces 2026-27 Club Licensing results as Indian football restructures. Sunil Chhetri's legacy as India's all-time top scorer endures — the next generation of Indian footballers looks to carry the torch he lit.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-23",
        },
        "sachin_rt": {
            "text": "The Master Blaster watches son Arjun Tendulkar play for Lucknow Super Giants in IPL 2026. Punjab Kings chased down 196 to beat LSG and keep their playoff hopes alive. Cricket's greatest legacy extends to the next generation on the biggest stage.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-23",
        },
        "SGanguly99": {
            "text": "Former BCCI president Saurav Ganguly watches IPL 2026's thrilling final day unfold. KKR — the franchise he built into champions — face DC at Eden Gardens tomorrow in a do-or-die battle for the 4th playoff spot. The Dada legacy looms large at his home ground.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-23",
        },
    }

    for handle, update in updates.items():
        if handle in leaders_by_handle:
            leaders_by_handle[handle]["text"] = update["text"]
            leaders_by_handle[handle]["url"] = update["url"]
            leaders_by_handle[handle]["date"] = update["date"]
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
            "caption": "RCB finish TOP of IPL 2026! Despite losing to SRH by 55 runs, Patidar's 56 and Krunal's 41* secured 1st place. Qualifier 1 vs Gujarat Titans on May 26 at Dharamsala. Three teams fight for the last spot on finals day tomorrow. The King's playoff campaign begins.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "PM Modi hosts US Secretary of State Marco Rubio in New Delhi — talks on trade, defense, energy, and Indo-Pacific. Rubio invites Modi to the White House. Quad FM meeting on May 26 in Delhi. Also this week: distributed 51,000 govt appointment letters and viral 'Melody' candy moment with Italian PM Meloni.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Jensen Huang",
            "handle": "nvidia",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Nvidia shatters records: $81.6 BILLION in Q1 revenue — 10x from 3 years ago. Unveils Vera Rubin platform with 10x inference throughput. Stock dips 1.8% as Dow hits record $50,579. Sees $1 trillion in orders ahead but concedes China chip market to Huawei.",
            "url": "https://www.instagram.com/nvidia/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Donald Trump",
            "handle": "realdonaldtrump",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Trump says Iran deal 'largely negotiated' — Strait of Hormuz to be reopened. Tells Axios: '50/50' between deal or blowing them 'to kingdom come.' 14-point MoU fine-tuned with Pakistan mediating. Tulsi Gabbard forced to resign as DNI — 4th Cabinet exit. VP Vance back in DC.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX files for potentially the world's LARGEST IPO ever — $1.25-2.2 trillion valuation. Starship's 12th test flight launches from Starbase. The world's richest person keeps pushing boundaries in space, AI, and EVs while the DOGE political chapter fades.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 8,000 jobs cut and 7,000 reassigned to AI teams. Leaked audio shows Zuck defending employee surveillance for the AI race. 'Success isn't a given.' Threads hits 150M daily users. No more company-wide layoffs in 2026 — for now.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat — Russian GM Nepomniachtchi fires: 'Every top GM would have a good chance against him.' Gukesh takes classical break to prepare for title defense against Sindarov later this year. The youngest world champion plots his comeback.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete with brother Anil. $1B telecom infrastructure investment, clean energy push, shares up 4.9%. The Ambani-Adani duopoly reshapes India's corporate landscape as $50B in Big Tech investment pours in.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "CSK eliminated from IPL 2026 playoffs. Captain Cool watches from sidelines as the final day unfolds — RR, PBKS, KKR fight for the 4th spot. Arjun Tendulkar debuted for LSG this season. The next generation plays on the biggest stage Dhoni helped build.",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' — SRK's ₹350 crore action thriller with daughter Suhana and Deepika — may split into two parts. Part 1 reportedly eyed for September 2026 release. Directed by Siddharth Anand. Bollywood's most ambitious film of the year takes shape.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika uses body double for action sequences in SRK's 'King' and Atlee's 'Raka' due to pregnancy. Filmed intense combat in Mumbai, climactic sequence planned for South Africa. Ranveer and Deepika back in town after celebrating her birthday in New York.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chairs 40+ nation Paris meeting with Macron on Strait of Hormuz security. Announces free summer bus travel for kids across England. Fends off Reform UK's Farage while defending EU alignment plans. Iran deal success critical for UK energy security.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MI face Rajasthan Royals at Wankhede tomorrow — final league match. It's a dead rubber for MI (4-9) but alive for RR: a win sends Rajasthan to playoffs. Hardik's all-round abilities tested in what could be a spoiler's paradise.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit's concert tour continues to sell out across North America — Vancouver the latest stop. The Punjabi superstar has become THE face of Indian music going global, bridging Bollywood and the diaspora one sold-out arena at a time.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, and data centers as $50B Big Tech investment wave hits India. Reliance-Adani rivalry intensifies after Ambani scraps noncompete. Rahul Gandhi renews political attacks over Modi-Adani ties.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka Chopra's dual Hollywood-Bollywood career continues. 'Jee Le Zaraa' with Katrina and Alia remains among the most anticipated films. Production slate grows as the ultimate NRI success story keeps breaking ceilings.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer's post-apocalyptic thriller 'Pralay' begins filming August 2026 with a massive ₹300 crore budget. Back in town with Deepika after her birthday trip to New York. Meanwhile Vicky Kaushal blocks 18 months for 'Mahavatar' — Bollywood bets big.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "The Master Blaster watches son Arjun play for Lucknow Super Giants in IPL 2026. Punjab Kings chased down 196/6 to beat LSG and keep playoff hopes alive. Cricket's greatest legacy extends to the next generation on the biggest stage.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President Ajay Banga shapes global development policy as India hosts Quad FM meeting and the Iran MoU nears finalization. Indian-American diaspora leaders now drive international economic governance at the highest levels.",
            "url": "https://www.instagram.com/ajay_banga/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress shares mountain retreat moments between projects. Shraddha's relatable content style continues to dominate social media — over 90M followers and counting.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Alia's 2026 slate packed with high-profile projects as she cements her position as Bollywood's most bankable actress. 'Jee Le Zaraa' with Priyanka and Katrina remains one of the most anticipated films of the year.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-23"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's live album generates buzz as her US concert tour hits 5 cities. The voice of a generation continues to sell out venues across the diaspora — bringing Bollywood's golden age of playback singing to NRI audiences worldwide.",
            "url": "https://www.instagram.com/shreyaghoshal/",
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
    print("✅ All pulse data updated for 2026-05-23 17:00 PDT")
