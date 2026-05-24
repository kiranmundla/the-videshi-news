#!/usr/bin/env python3
"""Power Pulse + Celebrity Buzz update — 2026-05-24 05:00 PDT
Key updates this cycle:
- IPL LIVE: MI vs RR at Wankhede — RR scored 192/8 in 20 overs, MI chasing
- KKR vs DC at Eden Gardens starts 7:30 PM IST (7:00 AM PDT) — not yet started
- Russia: confirmed ORESHNIK hypersonic missile used in massive Kyiv bombardment — 4+ killed, 50+ injured, NATO scrambled warplanes
- Iran deal: still 'largely negotiated' — Sunday finalization deadline holds; 60-day ceasefire extension, Hormuz no-toll passage, mine clearance, sanctions waivers
- White House shooting: Nasire Best (21, Maryland) confirmed dead — third incident near Trump in a month; had prior stay-away order
- Quad FM meeting confirmed for May 26 (Tuesday) in New Delhi — Rubio-Jaishankar bilateral already held Sunday
- Ramayana: prepone to Oct 30 confirmed; Namit Malhotra seeking ₹450 crore for Hindi distribution rights
- Rubio visited Kolkata (first US SecState visit in 14 years), then Delhi, Agra, Jaipur
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
            "text": "SpaceX IPO filing targets $1.75T valuation — largest ever if it closes. Iran deal 'largely negotiated' — Sunday finalization expected. If Hormuz reopens and oil drops, tech-heavy markets surge. Russia fires Oreshnik hypersonic missile at Kyiv — NATO scrambles warplanes. Dow near record ~50,563.",
            "url": "https://x.com/elonmusk",
            "date": "2026-05-24",
        },
        "zuck": {
            "text": "Meta confirms 15,000 job actions — 8K cut, 7K reassigned to AI. $115-135B AI infrastructure spend in 2026. Leaked audio: Zuckerberg defended employee surveillance. Threads crosses 150M daily users. White House shooting: Nasire Best (21) killed by Secret Service — third WH incident in a month.",
            "url": "https://x.com/zuck",
            "date": "2026-05-24",
        },
        "sundarpichai": {
            "text": "Google pushes Gemini AI across Search, Workspace, and Cloud. Rubio-Jaishankar bilateral held Sunday — tech cooperation central. Quad FM meeting Tuesday in Delhi. Big Tech's $50B India investment wave accelerates. Iran deal Sunday deadline — Hormuz reopening would lift global tech sentiment.",
            "url": "https://x.com/sundarpichai",
            "date": "2026-05-24",
        },
        "satyanadella": {
            "text": "Microsoft defends $80B AI infrastructure investment as Azure crosses $75B quarterly revenue. Copilot enterprise adoption at record highs. Russia fires Oreshnik hypersonic missile at Kyiv — geopolitical volatility rises. Iran deal Sunday finalization would stabilize energy markets and tech spending.",
            "url": "https://x.com/satyanadella",
            "date": "2026-05-24",
        },
        "sama": {
            "text": "Sam Altman teases GPT-5 — 'smarter than the smartest person' — as Musk v. OpenAI lawsuit heads toward trial. Bill Gates argues AI pauses counterproductive. Russia's Oreshnik hypersonic strike on Kyiv escalates tensions. Iran deal Sunday deadline could reshape global AI investment climate.",
            "url": "https://x.com/sama",
            "date": "2026-05-24",
        },
        "tim_cook": {
            "text": "Apple succession: John Ternus named — 'mind of an engineer, soul of an innovator.' WWDC 2026 AI features incoming. Apple asks Supreme Court to review App Store contempt ruling. White House shooting: third incident in a month raises security concerns across DC.",
            "url": "https://x.com/tim_cook",
            "date": "2026-05-24",
        },
        "nvidia": {
            "text": "Nvidia's jaw-dropping $81.6B Q1 revenue — 10x from three years ago. Vera Rubin platform: 10x inference throughput per megawatt over Blackwell. Jensen concedes China market to Huawei. Iran deal Sunday finalization + Hormuz reopening would lift markets further. Dow near record.",
            "url": "https://x.com/nvidia",
            "date": "2026-05-24",
        },
        "NandanNilekani": {
            "text": "Big Tech pours $50B into India. Rubio-Jaishankar bilateral Sunday — tech cooperation central to Quad agenda. Quad FM meeting Tuesday in Delhi. India emerging as top AI talent hub. Russia's Oreshnik strike on Kyiv and Iran deal add geopolitical dimension to India's tech moment.",
            "url": "https://x.com/NandanNilekani",
            "date": "2026-05-24",
        },
        "BillGates": {
            "text": "Bill Gates argues AI pauses risk ceding ground to less safety-conscious actors. Kevin Warsh starts at the Fed. Russia fires Oreshnik hypersonic missile at Kyiv — NATO scrambles warplanes, 4+ killed, 50+ injured. Iran deal 'largely negotiated' — Sunday finalization deadline holds.",
            "url": "https://x.com/BillGates",
            "date": "2026-05-24",
        },
        "ArvindKrishna": {
            "text": "IBM CEO expands AI partnerships — Tech Mahindra and IBM accelerate enterprise GenAI via watsonx. India emerges as major enterprise AI hub. Rubio-Jaishankar bilateral Sunday; Quad FM meeting Tuesday. $50B Big Tech India wave. IPL's dramatic final day captivates the nation.",
            "url": "https://x.com/ArvindKrishna",
            "date": "2026-05-24",
        },
        "ShantanuNarayen": {
            "text": "Adobe CEO integrates generative AI across Creative Cloud. Firefly gains traction against Midjourney and DALL-E. Cannes 2026 closed — 'Fjord' won Palme d'Or as AI-generated content debate intensifies. Ramayana may prepone to Oct 30 — ₹450 crore distribution rights sought.",
            "url": "https://x.com/ShantanuNarayen",
            "date": "2026-05-24",
        },
        "paraga": {
            "text": "Former Twitter CEO Parag Agrawal focuses on AI ventures and advisory roles post-Musk acquisition. Indian-American tech diaspora shapes global AI leadership as Big Tech pours $50B into India. Quad FM meeting Tuesday in Delhi cements India's tech diplomacy moment.",
            "url": "https://x.com/paraga",
            "date": "2026-05-21",
        },
        "LeenaNairHR": {
            "text": "Chanel CEO Leena Nair steers luxury house through competitive landscape. Cannes 2026 wrapped — Aishwarya dazzled, Aaradhya's red carpet debut. Ramayana preponed to Oct 30 (Diwali week), ₹450 crore Hindi rights. Indian diaspora influence in luxury leadership grows.",
            "url": "https://x.com/LeenaNairHR",
            "date": "2026-05-24",
        },
        "RajSubramaniam": {
            "text": "FedEx CEO navigates logistics amid trade disruptions. Iran deal 'largely negotiated' — Hormuz reopening transformative for global shipping. Pakistan's Quetta bomb killed 24. Russia's Oreshnik strike on Kyiv escalates — NATO warplanes scrambled. Quad FM meeting Tuesday.",
            "url": "https://x.com/RajSubramaniam",
            "date": "2026-05-24",
        },

        # === INDIA PULSE ===
        "narendramodi": {
            "text": "Rubio-Jaishankar bilateral held SUNDAY — discussed Middle East, trade, defense, visas, maritime security. 'Progress in last 48 hours' on Iran. Trump invites Modi to White House. 'Mission 500' to double trade by 2030. Quad FM Meeting TUESDAY in Delhi. India at center of global diplomacy.",
            "url": "https://x.com/narendramodi",
            "date": "2026-05-24",
        },
        "PMOIndia": {
            "text": "India-US ties deepen — Rubio's 4-city visit (Kolkata → Delhi → Agra → Jaipur), first US SecState in Kolkata in 14 years. Quad FM meeting Tuesday. Iran deal 'largely negotiated' — Sunday deadline. Russia fires Oreshnik at Kyiv. India positioned as key player in global diplomacy.",
            "url": "https://x.com/PMOIndia",
            "date": "2026-05-24",
        },
        "AmitShah": {
            "text": "Home Minister Shah oversees national security as White House shooting (Nasire Best, 21, killed) and Pakistan's Quetta bombing (24 dead) underline global security challenges. Russia's Oreshnik hypersonic strike on Kyiv kills 4+. Rubio-Jaishankar bilateral discussed counter-terrorism.",
            "url": "https://x.com/AmitShah",
            "date": "2026-05-24",
        },
        "RahulGandhi": {
            "text": "Congress leader renews attacks on Modi-Adani ties as Adani Group expands. Opposition sharpens criticism amid $50B Big Tech wave and $22.2B FPI outflows. Rubio's White House invite to Modi draws attention. IPL LIVE: MI chase RR's 192/8 at Wankhede — drama guaranteed.",
            "url": "https://x.com/RahulGandhi",
            "date": "2026-05-24",
        },
        "myogiadityanath": {
            "text": "UP CM Yogi continues infrastructure push. Rubio's Kolkata visit — first US SecState in 14 years — expands diplomatic footprint beyond Delhi. Rajamouli's 'Varanasi' (Mahesh Babu) shoots key song in UP — global spotlight on the holy city. IPL's dramatic final day captivates India.",
            "url": "https://x.com/myogiadityanath",
            "date": "2026-05-24",
        },
        "ArvindKejriwal": {
            "text": "AAP leader Kejriwal steps up opposition rhetoric. Iran deal reaches Sunday deadline. IPL LIVE: MI chase RR's 192/8 at Wankhede — if MI win, PBKS get the 4th playoff spot. KKR vs DC at Eden Gardens tonight decides the rest. The most dramatic IPL final day ever.",
            "url": "https://x.com/ArvindKejriwal",
            "date": "2026-05-24",
        },
        "DrSJaishankar": {
            "text": "EAM Jaishankar held bilateral with Rubio SUNDAY — discussed Middle East, trade, visas, maritime security, energy. Rubio: 'progress in last 48 hours' on Iran. Quad FM Meeting TUESDAY with US, Japan, Australia FMs in Delhi. India's diplomatic moment of the year.",
            "url": "https://x.com/DrSJaishankar",
            "date": "2026-05-24",
        },
        "nsitharaman": {
            "text": "FM Sitharaman monitors economic outlook — $50B Big Tech investments land while FPI outflows hit $22.2B. Iran deal Sunday finalization could ease oil import costs. Russia's Oreshnik strike on Kyiv and Quetta bombing add geopolitical risk. Dow near record ~50,563.",
            "url": "https://x.com/nsitharaman",
            "date": "2026-05-24",
        },
        "rashtrapatibhvn": {
            "text": "President Murmu presides as India hosts critical Quad diplomacy. Rubio-Jaishankar bilateral completed Sunday. Quad FM meeting Tuesday in Delhi with US, Japan, Australia. Iran deal 'largely negotiated.' Russia fires Oreshnik at Kyiv. India's global standing strengthens.",
            "url": "https://x.com/rashtrapatibhvn",
            "date": "2026-05-24",
        },
        "gautam_adani": {
            "text": "Adani Group pushes into green energy, ports, data centers as India attracts $50B Big Tech wave. Reliance-Adani rivalry intensifies after Ambani scraps family noncompete. Iran deal Sunday deadline — Hormuz reopening could reshape India's entire energy import chain.",
            "url": "https://x.com/gautam_adani",
            "date": "2026-05-24",
        },
        "RelianceJio": {
            "text": "Mukesh Ambani's Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment, shares up 4.9%. Iran deal Sunday finalization expected. MI vs RR LIVE at Wankhede — Ambani's team chasing RR's 192/8. The most dramatic IPL final day.",
            "url": "https://x.com/RelianceJio",
            "date": "2026-05-24",
        },
        "RNTata2000": {
            "text": "The Ratan Tata Foundation continues its philanthropy legacy. Tata Group at forefront as India attracts record foreign investment. Russia's Oreshnik hypersonic strike on Kyiv kills 4+ — NATO scrambles warplanes. Quad FM meeting Tuesday elevates India's global role.",
            "url": "https://x.com/RNTata2000",
            "date": "2026-05-24",
        },

        # === WORLD / POWER PULSE ===
        "realDonaldTrump": {
            "text": "Iran deal 'LARGELY NEGOTIATED' — Sunday finalization expected. 60-day ceasefire, Hormuz no-toll passage, mine clearance, sanctions waivers on the table. White House shooting: Nasire Best (21, Maryland) killed by Secret Service — third WH incident in a month. Trump safe; praised 'swift action.'",
            "url": "https://x.com/realDonaldTrump",
            "date": "2026-05-24",
        },
        "WhiteHouse": {
            "text": "SHOOTING: Nasire Best, 21 (Maryland), killed by Secret Service after opening fire at WH checkpoint. Had prior stay-away order. Third WH incident in a month. Bystander wounded. Trump safe. Iran deal 'largely negotiated' — Sunday deadline. Gabbard exited DNI; Aaron Lukas acting.",
            "url": "https://x.com/WhiteHouse",
            "date": "2026-05-24",
        },
        "Keir_Starmer": {
            "text": "UK PM co-chaired 40+ nation Hormuz summit with Macron. Iran deal Sunday finalization imminent. Russia fires ORESHNIK hypersonic missile at Kyiv — 4+ killed, 50+ injured, NATO scrambles warplanes. Dual crisis management: Iran peace + Ukraine escalation. Reform UK's Farage sharpens attacks.",
            "url": "https://x.com/Keir_Starmer",
            "date": "2026-05-24",
        },
        "EmmanuelMacron": {
            "text": "Macron co-hosted 40+ nation Hormuz summit. Iran deal Sunday finalization imminent. Russia fires Oreshnik hypersonic missile at Kyiv — 4+ killed, 50+ injured, NATO scrambles warplanes. France navigates dual crises: Iran peace + Ukraine escalation. Oil at ~$107.",
            "url": "https://x.com/EmmanuelMacron",
            "date": "2026-05-24",
        },
        "AlboMP": {
            "text": "Australian PM Albanese prepares for Quad FM meeting in New Delhi TUESDAY. Iran deal Sunday finalization expected. Russia's Oreshnik hypersonic strike escalates Ukraine war. Australia's FM to engage India, Japan, US on Indo-Pacific security. Hormuz resolution affects energy costs.",
            "url": "https://x.com/AlboMP",
            "date": "2026-05-24",
        },
        "GiorgiaMeloni": {
            "text": "Italian PM Meloni's 'Melody' bond with Modi strengthens Italy-India ties. Iran deal Sunday deadline. Russia fires Oreshnik hypersonic missile at Kyiv — 4+ killed, NATO scrambles warplanes. G7 coordination on Iran and Ukraine intensifies. Quetta bombing (24 dead) adds urgency.",
            "url": "https://x.com/GiorgiaMeloni",
            "date": "2026-05-24",
        },
        "HHShkMohd": {
            "text": "UAE ruler MBR watches Iran deal finalization — Sunday deadline. 60-day ceasefire extension, no-toll Hormuz passage, mine clearance proposed. US blockade lift + sanctions waivers for oil on table. ADNOC: full oil flows not before Q1 2027 even if deal holds. Gulf stability at stake.",
            "url": "https://x.com/HHShkMohd",
            "date": "2026-05-24",
        },
        "chrisluxonNZ": {
            "text": "NZ PM Luxon monitors Indo-Pacific developments as Quad FM meeting approaches Tuesday. Iran deal Sunday deadline. Russia's Oreshnik hypersonic strike on Kyiv escalates Ukraine war — NATO scrambles warplanes. Five Eyes alignment shifts as multiple crises converge.",
            "url": "https://x.com/chrisluxonNZ",
            "date": "2026-05-24",
        },
        "VivekGRamaswamy": {
            "text": "Vivek continues post-DOGE political trajectory. Gabbard resigned as DNI (husband's cancer) — Aaron Lukas acting. White House shooting: Nasire Best (21) killed — third WH incident in a month, had prior stay-away order. Vivek's Ohio ambitions and 2028 positioning continue.",
            "url": "https://x.com/VivekGRamaswamy",
            "date": "2026-05-24",
        },
        "RishiSunak": {
            "text": "Former UK PM Sunak observes from opposition as Starmer navigates Iran deal and Russia's Oreshnik hypersonic strike on Kyiv. NATO scrambles warplanes. Reform UK's Farage sharpens attacks. Sunak's legacy as Britain's first Indian-origin PM resonates with the global diaspora.",
            "url": "https://x.com/RishiSunak",
            "date": "2026-05-24",
        },
        "UshaVance": {
            "text": "Second Lady Usha Vance — Indian-American Yale Law grad — watches as VP JD Vance returned to DC for Iran deal deliberations. White House shooting: Nasire Best killed near checkpoint where Vance's motorcade passes. Third WH incident in a month. Iran deal Sunday finalization imminent.",
            "url": "https://x.com/UshaVance",
            "date": "2026-05-24",
        },
        "KashPatel47": {
            "text": "FBI Director Kash Patel oversees investigation into White House shooting — Nasire Best, 21 (Maryland), had prior stay-away order and 'violent history.' Third WH incident in a month. FBI probing motive. Iran deal Sunday deadline keeps intelligence community active.",
            "url": "https://x.com/KashPatel47",
            "date": "2026-05-24",
        },
        "SriramKrishnan": {
            "text": "White House AI advisor Sriram Krishnan shapes US tech policy amid $50B Big Tech India push and SpaceX's $1.75T IPO filing. Rubio-Jaishankar bilateral Sunday — tech cooperation central. Quad FM meeting Tuesday. WH shooting raises security concerns near AI policy offices.",
            "url": "https://x.com/SriramKrishnan",
            "date": "2026-05-24",
        },
        "SuellaBraverman": {
            "text": "Former UK Home Secretary Suella Braverman — Indian-origin Tory — vocal on immigration from backbenches. Russia's Oreshnik hypersonic strike on Kyiv and White House shooting dominate headlines. Starmer faces Reform UK pressure. Quad FM meeting Tuesday in Delhi.",
            "url": "https://x.com/SuellaBraverman",
            "date": "2026-05-24",
        },
        "AjayBanga": {
            "text": "World Bank President Ajay Banga monitors Iran deal Sunday finalization — Hormuz reopening would transform global trade. Russia's Oreshnik strike on Kyiv kills 4+, NATO scrambles warplanes. ADNOC warns full oil flows won't return before Q1 2027. Quetta bombing (24 dead) adds instability.",
            "url": "https://x.com/AjayBanga",
            "date": "2026-05-24",
        },

        # === SPORTS PULSE ===
        "imVkohli": {
            "text": "IPL FINAL DAY: RCB finished TOP with 18 pts (best NRR). Qualifier 1 vs GT May 27 at Dharamsala. LIVE NOW: MI chase RR's 192/8 at Wankhede — if MI win, PBKS qualify. KKR vs DC at Eden Gardens 7:30 PM IST. Three teams, one spot. Kohli watches from the top.",
            "url": "https://x.com/imVkohli",
            "date": "2026-05-24",
        },
        "ImRo45": {
            "text": "IPL LIVE: MI chasing RR's 192/8 at Wankhede! RR elected to bat (MI won toss, chose to bowl). MI's dead rubber is RR's knockout — if MI win, PBKS get the 4th spot. Rohit's last match of the season decides three teams' fates. The biggest 'meaningless' match in IPL history.",
            "url": "https://x.com/ImRo45",
            "date": "2026-05-24",
        },
        "msdhoni": {
            "text": "CSK eliminated from IPL 2026. LIVE NOW: MI chase RR's 192/8 at Wankhede. KKR vs DC at Eden Gardens 7:30 PM IST. PBKS (15 pts) need RR AND KKR to lose. RR's 192/8 — can MI run it down? The IPL Dhoni helped build has never been this dramatic.",
            "url": "https://x.com/msdhoni",
            "date": "2026-05-24",
        },
        "Jaspritbumrah93": {
            "text": "IPL LIVE: MI chasing RR's 192/8 at Wankhede! MI won toss, chose to bowl. Bumrah left out of T20 World Cup squad — managed for longer formats. MI's dead rubber holds three teams' fates. Can Bumrah's team play kingmaker on the most dramatic IPL final day?",
            "url": "https://x.com/Jaspritbumrah93",
            "date": "2026-05-24",
        },
        "hardikpandya7": {
            "text": "IPL LIVE: MI chasing RR's 192/8 at Wankhede (3:30 PM IST). MI won toss, chose to bowl — RR batted first. If MI win, PBKS get the 4th spot. Hardik's MI hold three teams' fates. Pride match becomes kingmaker showdown. The most dramatic IPL final day ever.",
            "url": "https://x.com/hardikpandya7",
            "date": "2026-05-24",
        },
        "BCCI": {
            "text": "IPL 2026 FINAL DAY LIVE: Match 69 MI vs RR at Wankhede — RR scored 192/8, MI chasing. Match 70 KKR vs DC at Eden Gardens 7:30 PM IST. Top 3 locked: RCB (1st), GT (2nd), SRH (3rd). PBKS (15 pts) pray for RR AND KKR losses. RR (14) just needed a win. KKR (13) need win + RR loss.",
            "url": "https://x.com/BCCI",
            "date": "2026-05-24",
        },
        "ICC": {
            "text": "ICC board meeting in Ahmedabad May 30. IPL LIVE: MI chase RR's 192/8 at Wankhede — three teams fight for one playoff spot. Kohli-Head handshake controversy still viral globally. T20 World Cup squad selections create ripples. Cricket at fever pitch.",
            "url": "https://x.com/ICC",
            "date": "2026-05-24",
        },
        "IPL": {
            "text": "FINAL DAY LIVE: Match 69 MI vs RR at Wankhede — RR posted 192/8, MI chasing! Match 70 KKR vs DC at Eden Gardens 7:30 PM IST. Three teams, one spot. PBKS (15 pts). RR (14) — need to win. KKR (13) — need win + RR loss. Playoffs start May 27 at Dharamsala.",
            "url": "https://x.com/IPL",
            "date": "2026-05-24",
        },
        "Neeraj_chopra1": {
            "text": "Neeraj Chopra preps for 2026 athletics season. Federation Cup in Ranchi spotlights India's next wave of track and field talent. Diamond League awaits the Olympic champion's return. IPL LIVE: MI chase RR's 192/8 — the nation watches.",
            "url": "https://x.com/Neeraj_chopra1",
            "date": "2026-05-24",
        },
        "Pvsindhu1": {
            "text": "PV Sindhu continues badminton campaign as the international circuit heats up. India's shuttlers build momentum through Super Series events ahead of the Asian Games cycle.",
            "url": "https://x.com/Pvsindhu1",
            "date": "2026-05-22",
        },
        "MirzaSania": {
            "text": "Tennis icon Sania Mirza's legacy inspires Indian tennis. Post-retirement, she remains the most prominent Indian face in global tennis, mentoring the next generation.",
            "url": "https://x.com/MirzaSania",
            "date": "2026-05-22",
        },
        "DGukesh": {
            "text": "World Chess Champion D Gukesh faces heat — GM Nepomniachtchi: 'Every top GM would have a good chance against him.' Preps for title defense against Sindarov. IPL LIVE: MI chase RR's 192/8 at Wankhede. Iran deal Sunday deadline. India's dramatic Sunday.",
            "url": "https://x.com/DGukesh",
            "date": "2026-05-24",
        },
        "chetrisunil11": {
            "text": "AIFF announces 2026-27 Club Licensing results as Indian football restructures. Sunil Chhetri's legacy as India's all-time top scorer endures. IPL LIVE: MI chase RR's 192/8 — the most dramatic final day in IPL history.",
            "url": "https://x.com/chetrisunil11",
            "date": "2026-05-24",
        },
        "sachin_rt": {
            "text": "Son Arjun's LSG fell to PBKS last night (Shreyas Iyer 101*). LIVE NOW: MI chase RR's 192/8 at Wankhede — the match that decides the 4th playoff spot. KKR vs DC at Eden Gardens follows. Three teams, one seat. Cricket's greatest legacy meets IPL's most dramatic day.",
            "url": "https://x.com/sachin_rt",
            "date": "2026-05-24",
        },
        "SGanguly99": {
            "text": "DADA'S KKR face DC at Eden Gardens TONIGHT (7:30 PM IST) — do-or-die for the 4th spot. KKR need to win AND hope MI beat RR. LIVE: MI chasing RR's 192/8 at Wankhede — if RR win, KKR are out regardless. The most dramatic IPL final day. Three teams, one spot.",
            "url": "https://x.com/SGanguly99",
            "date": "2026-05-24",
        },
    }

    for handle, update in updates.items():
        if handle in leaders_by_handle:
            leader = leaders_by_handle[handle]
            if "latestPost" in leader:
                leader["latestPost"]["text"] = update["text"]
                leader["latestPost"]["url"] = update["url"]
                leader["latestPost"]["date"] = update["date"]
            if "text" in leader:
                leader["text"] = update["text"]
            if "url" in leader:
                leader["url"] = update["url"]
            if "date" in leader:
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
            "caption": "Iran deal 'LARGELY NEGOTIATED' — Sunday finalization expected. 60-day ceasefire, Hormuz no-toll passage, mine clearance, sanctions waivers. White House SHOOTING: Nasire Best (21, Maryland) killed by Secret Service — third WH incident in a month. Trump safe.",
            "url": "https://www.instagram.com/realdonaldtrump/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Virat Kohli",
            "handle": "virat.kohli",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "IPL FINAL DAY: RCB top with 18 pts, Qualifier 1 vs GT May 27 at Dharamsala. LIVE NOW: MI chase RR's 192/8 at Wankhede — if MI win, PBKS qualify. KKR vs DC at Eden Gardens 7:30 PM IST. Three teams, one seat. Kohli watches from the top of the table.",
            "url": "https://www.instagram.com/virat.kohli/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Narendra Modi",
            "handle": "narendramodi",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Rubio-Jaishankar bilateral held SUNDAY — Middle East, trade, visas, maritime security. 'Progress in last 48 hours' on Iran. Quad FM Meeting TUESDAY in Delhi. Trump invites Modi to White House. 'Mission 500' to double trade. India at center of global diplomacy.",
            "url": "https://www.instagram.com/narendramodi/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreyas Iyer",
            "handle": "shreyasiyer96",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "MAIDEN IPL CENTURY (101*) lifts PBKS to 15 pts. The agonizing wait: LIVE NOW — MI chasing RR's 192/8 at Wankhede. PBKS need MI to win AND KKR to lose to DC tonight. Iyer did his part — can MI deliver the knockout?",
            "url": "https://www.instagram.com/shreyasiyer96/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Aishwarya Rai Bachchan",
            "handle": "aaborofficial",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Cannes 2026 wrapped — Aishwarya dazzled in Amit Aggarwal couture, Aaradhya's red carpet debut stole hearts. 'Fjord' won Palme d'Or. Ramayana preponed to Oct 30 (Diwali week) — Namit Malhotra seeks ₹450 crore for Hindi distribution rights alone. Red carpet scam exposé rocks festival.",
            "url": "https://www.instagram.com/aaborofficial/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Elon Musk",
            "handle": "elonmusk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "SpaceX IPO targets $1.75T — potentially LARGEST ever. Iran deal Sunday finalization expected. Russia fires Oreshnik hypersonic missile at Kyiv — NATO scrambles warplanes. If Hormuz reopens, oil drops, tech soars. Dow near record ~50,563.",
            "url": "https://www.instagram.com/elonmusk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mark Zuckerberg",
            "handle": "zuck",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Meta's AI reckoning: 15K job actions (8K cut + 7K reassigned). $115-135B on AI infra in 2026. Leaked audio: Zuck defends surveillance for AI race. Threads hits 150M daily. WH shooting: third incident in a month. Russia fires Oreshnik at Kyiv.",
            "url": "https://www.instagram.com/zuck/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shah Rukh Khan",
            "handle": "iamsrk",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'King' with Suhana and Deepika may split into two parts — Part 1 eyed for Christmas 2026. KKR face DC at Eden Gardens TONIGHT 7:30 PM IST — SRK's team needs a miracle. LIVE: MI chasing RR's 192/8 at Wankhede — if RR win, KKR are out. Dhurandhar at ₹1,307 crore.",
            "url": "https://www.instagram.com/iamsrk/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "MS Dhoni",
            "handle": "msdhoni",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "CSK eliminated. LIVE NOW: MI chase RR's 192/8 at Wankhede. KKR vs DC at Eden Gardens 7:30 PM IST. Three teams, one spot. PBKS need both RR and KKR to lose. The IPL Dhoni helped build has never been more dramatic. Who gets the 4th seat?",
            "url": "https://www.instagram.com/msdhoni/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Hardik Pandya",
            "handle": "hardikpandya93",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "IPL LIVE: MI chasing RR's 192/8 at Wankhede (3:30 PM IST). MI won toss, chose to bowl. If MI win, PBKS get the 4th spot. Hardik's MI hold three teams' fates. Pride match becomes kingmaker showdown. The most dramatic IPL final day in history.",
            "url": "https://www.instagram.com/hardikpandya93/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Deepika Padukone",
            "handle": "deepikapadukone",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Deepika uses body double for action in SRK's 'King' and Atlee's 'Raka' due to pregnancy. Ramayana preponed to Oct 30 (Diwali week) — ₹450 crore Hindi rights. 'Varanasi' (Rajamouli/Mahesh Babu) shoots key song. Bollywood's biggest year takes shape.",
            "url": "https://www.instagram.com/deepikapadukone/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Diljit Dosanjh",
            "handle": "diljitdosanjh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Diljit's concert tour sells out across North America. THE face of Indian music going global — bridging Bollywood and the diaspora. 6 featured events on The Videshi. IPL LIVE: MI chase RR's 192/8 as nation watches. Iran deal Sunday deadline looms.",
            "url": "https://www.instagram.com/diljitdosanjh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ranveer Singh",
            "handle": "ranveersingh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Ranveer's 'Pralay' (₹300 crore post-apocalyptic thriller) begins filming August 2026. Dhurandhar at ₹1,307 crore. Ramayana preponed to Oct 30 — ₹450 crore Hindi rights sought. Vicky Kaushal blocks 18 months for 'Mahavatar.' Bollywood's biggest-ever year.",
            "url": "https://www.instagram.com/ranveersingh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Sachin Tendulkar",
            "handle": "sachintendulkar",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Son Arjun's LSG fell last night (Shreyas Iyer 101*). LIVE NOW: MI chase RR's 192/8 at Wankhede — decides three teams' fates. KKR vs DC at Eden Gardens follows. The greatest IPL final day — three teams, one spot. Cricket's legacy meets its most dramatic moment.",
            "url": "https://www.instagram.com/sachintendulkar/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "D Gukesh",
            "handle": "dgukesh",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Chess Champion faces heat — GM Nepo: 'Every top GM would have a good chance against him.' Preps for title defense against Sindarov. IPL LIVE: MI chase RR's 192/8. Iran deal Sunday deadline. Russia fires Oreshnik at Kyiv. India's dramatic Sunday.",
            "url": "https://www.instagram.com/dgukesh/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Mukesh Ambani",
            "handle": "reliancejio",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Reliance expands into power and telecom after scrapping family noncompete. $1B telecom investment. Iran deal Sunday finalization expected. MI vs RR LIVE at Wankhede — Ambani's team chasing RR's 192/8, playing kingmaker for three teams.",
            "url": "https://www.instagram.com/reliancejio/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Priyanka Chopra",
            "handle": "priyankachopra",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Global icon Priyanka's dual Hollywood-Bollywood career continues. 'Jee Le Zaraa' with Katrina and Alia most anticipated. Ramayana preponed to Oct 30 — ₹450 crore Hindi rights. Cannes wrapped with red carpet scam exposé. Indian star power going global.",
            "url": "https://www.instagram.com/priyankachopra/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shreya Ghoshal",
            "handle": "shreyaghoshal",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Shreya Ghoshal's live album generates buzz as US tour hits 5 cities. The voice of a generation sells out diaspora venues — bringing Bollywood's golden age to NRI audiences. IPL LIVE: MI chase RR's 192/8 as India's most dramatic Sunday unfolds.",
            "url": "https://www.instagram.com/shreyaghoshal/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Shraddha Kapoor",
            "handle": "shraddhakapoor",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Instagram's most-followed Indian actress (90M+). Cannes 2026 wrapped — red carpet scam exposé reveals paid access industry. Ramayana preponed to Oct 30 — ₹450 crore Hindi rights. Bollywood's biggest year continues to take shape.",
            "url": "https://www.instagram.com/shraddhakapoor/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Alia Bhatt",
            "handle": "aliaabhatt",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "'Jee Le Zaraa' with Priyanka and Katrina most anticipated. IMAX confirms Ranbir's 'Ramayana' — preponed to Oct 30 (Diwali week), ₹450 crore Hindi rights sought. 'Varanasi' (Rajamouli/Mahesh Babu) shoots key song. Bollywood's biggest slate ever.",
            "url": "https://www.instagram.com/aliaabhatt/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Gautam Adani",
            "handle": "gautam_adani",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "Adani Group pushes into green energy, ports, data centers. $50B Big Tech wave hits India. Iran deal Sunday deadline — Hormuz reopening could reshape India's energy import chain. Reliance-Adani rivalry intensifies. Russia fires Oreshnik at Kyiv.",
            "url": "https://www.instagram.com/gautam_adani/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Keir Starmer",
            "handle": "keir_starmer",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "UK PM co-chaired 40+ nation Hormuz summit. Iran deal Sunday finalization imminent. Russia fires Oreshnik hypersonic missile at Kyiv — 4+ killed, NATO scrambles warplanes. Dual crisis management. Free summer bus travel for kids. Reform UK sharpens attacks.",
            "url": "https://www.instagram.com/keir_starmer/",
            "media_type": "image",
            "timestamp": "2026-05-24"
        },
        {
            "name": "Ajay Banga",
            "handle": "ajay_banga",
            "platform": "instagram",
            "thumbnail": "",
            "caption": "World Bank President monitors Iran deal Sunday finalization — Hormuz reopening transforms global trade. Russia fires Oreshnik hypersonic missile — NATO scrambles. ADNOC: full oil flows not before Q1 2027. Indian-American diaspora at helm of global governance.",
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
    print("✅ All pulse data updated for 2026-05-24 05:00 PDT")
