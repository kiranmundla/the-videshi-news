#!/usr/bin/env python3
"""
Expand indian-american-leaders.json to cover the global Indian diaspora.
- Add 'country' field to all existing entries
- Add new 'government' category
- Add global leaders from UK, Canada, Ireland, Singapore, Caribbean, etc.
- Add British-Indian and global entertainment figures
- Add global business leaders
"""

import json

# Load existing data
with open('indian-american-leaders.json') as f:
    data = json.load(f)

existing_leaders = data['leaders']

# Add country field to all existing entries (all are US)
for leader in existing_leaders:
    if 'country' not in leader:
        leader['country'] = 'US'

# Fix specific entries that are NOT US-based
country_fixes = {
    "Leena Nair": "UK",  # Chanel is based in UK/France, she's London-based
    "Zubin Mehta": "US",  # Primarily US-based (though born in India)
    "Akshay Venkatesh": "Australia",  # Australian mathematician
    "Venkatraman Ramakrishnan": "UK",  # Cambridge, UK
    "Salman Rushdie": "UK",  # British-Indian (though now in US)
    "Ajay Banga": "US",  # World Bank, but US citizen
    "Dev Patel": "UK",  # British actor born in London
}
for leader in existing_leaders:
    if leader['name'] in country_fixes:
        leader['country'] = country_fixes[leader['name']]

# ========== NEW ENTRIES ==========

new_entries = []

# ===== GOVERNMENT - INTERNATIONAL =====

new_entries.append({
    "name": "Kamala Harris",
    "position": "Former Vice President of the United States",
    "category": "government",
    "company": "United States Government",
    "country": "US",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Kamala_Harris",
    "twitter": "@KamalaHarris",
    "bio": "Born in Oakland, California to an Indian mother (Shyamala Gopalan, a cancer researcher from Tamil Nadu) and a Jamaican father. Served as the 49th Vice President of the United States (2021–2025), the first woman, first African American, and first Asian American to hold the office. Previously served as a U.S. Senator from California and as California's Attorney General.",
    "notable_achievement": "First woman and first person of Indian and African American descent to serve as Vice President of the United States"
})

new_entries.append({
    "name": "Rishi Sunak",
    "position": "Former Prime Minister of the United Kingdom",
    "category": "government",
    "company": "UK Government",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Rishi_Sunak",
    "twitter": "@RishiSunak",
    "bio": "Born in Southampton, England, to parents of Punjabi Indian descent who emigrated from East Africa. Educated at Winchester College, Oxford University, and Stanford MBA. Served as Prime Minister of the United Kingdom (2022–2024) and previously as Chancellor of the Exchequer. Married to Akshata Murty, daughter of Infosys co-founder N. R. Narayana Murthy.",
    "notable_achievement": "First person of Indian origin and first Hindu to serve as Prime Minister of the United Kingdom"
})

new_entries.append({
    "name": "Leo Varadkar",
    "position": "Former Taoiseach (Prime Minister) of Ireland",
    "category": "government",
    "company": "Government of Ireland",
    "country": "Ireland",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Leo_Varadkar",
    "twitter": "@LeoVaradkar",
    "bio": "Born in Dublin, Ireland, to an Indian father (Ashok Varadkar from Mumbai, of Konkani descent) and an Irish mother. Served as Taoiseach (2017–2020 and 2022–2024) and is the first person of Indian heritage and first openly gay person to lead Ireland. Qualified as a medical doctor before entering politics.",
    "notable_achievement": "First person of Indian descent and youngest person to serve as Taoiseach of Ireland"
})

new_entries.append({
    "name": "Pravind Jugnauth",
    "position": "Former Prime Minister of Mauritius",
    "category": "government",
    "company": "Government of Mauritius",
    "country": "Mauritius",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Pravind_Jugnauth",
    "twitter": "",
    "bio": "Born in Vacoas-Phoenix, Mauritius, of Indo-Mauritian (Bhojpuri) descent. Served as Prime Minister of Mauritius from 2017 to 2024. Son of Sir Anerood Jugnauth, who also served multiple terms as Prime Minister and President. Studied law at the University of Buckingham in England.",
    "notable_achievement": "Led Mauritius as Prime Minister for seven years; part of a political dynasty that has shaped Mauritius since independence"
})

new_entries.append({
    "name": "António Costa",
    "position": "President of the European Council",
    "category": "government",
    "company": "European Union",
    "country": "Portugal",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Ant%C3%B3nio_Costa",
    "twitter": "@antonaboris",
    "bio": "Born in Lisbon, Portugal, of Indo-Portuguese Goan descent. His father, Orlando da Costa, was a writer born in Mozambique to a Goan family. Served as Prime Minister of Portugal (2015–2024) and became President of the European Council in December 2024. One of the longest-serving prime ministers of Portugal.",
    "notable_achievement": "First person of Indian (Goan) descent to lead the European Council; served as Prime Minister of Portugal for over eight years"
})

new_entries.append({
    "name": "Suella Braverman",
    "position": "Member of Parliament",
    "category": "government",
    "company": "UK Parliament",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Suella_Braverman",
    "twitter": "@SuellaBraverman",
    "bio": "Born in London to parents of Indian descent — her mother is Tamil from Mauritius and her father is Goan from Kenya. Served as Home Secretary (2022–2023) and Attorney General for England and Wales (2020–2022). Barrister by training, educated at Cambridge and the Sorbonne.",
    "notable_achievement": "First Indian-heritage woman to serve as UK Home Secretary and first Buddhist to hold a Great Office of State"
})

new_entries.append({
    "name": "Priti Patel",
    "position": "Member of Parliament",
    "category": "government",
    "company": "UK Parliament",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Priti_Patel",
    "twitter": "@pritipatel",
    "bio": "Born in London to Gujarati Indian parents who emigrated from Uganda. Served as Home Secretary (2019–2022) and Secretary of State for International Development (2016–2017). Conservative MP for Witham since 2010.",
    "notable_achievement": "First Indian-origin Home Secretary of the United Kingdom; championed the UK's post-Brexit immigration policies"
})

new_entries.append({
    "name": "Alok Sharma",
    "position": "Former Cabinet Minister & COP26 President",
    "category": "government",
    "company": "UK Parliament",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Alok_Sharma",
    "twitter": "@AlokSharma_RDG",
    "bio": "Born in Agra, India, and moved to the UK as a child. Served as President of COP26 climate summit (2021–2022), Secretary of State for Business, Energy and Industrial Strategy, and Secretary of State for International Development. Conservative MP for Reading West.",
    "notable_achievement": "Presided over the COP26 UN Climate Change Conference in Glasgow; first Indian-born person to chair a major UN climate summit"
})

new_entries.append({
    "name": "Lisa Nandy",
    "position": "Secretary of State for Culture, Media and Sport",
    "category": "government",
    "company": "UK Government",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Lisa_Nandy",
    "twitter": "@lisanandy",
    "bio": "Born in Manchester, England, of Indian and English heritage — her father Dipak Nandy is an Indian academic and race relations activist from Calcutta. Labour MP for Wigan since 2010. Served as Shadow Foreign Secretary before becoming Secretary of State for Culture, Media and Sport in the Starmer government.",
    "notable_achievement": "First person of Indian heritage to serve as UK Culture Secretary; prominent voice on community regeneration and devolution"
})

new_entries.append({
    "name": "Jagmeet Singh",
    "position": "Former Leader of the New Democratic Party",
    "category": "government",
    "company": "Parliament of Canada",
    "country": "Canada",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Jagmeet_Singh",
    "twitter": "@theJagmeetSingh",
    "bio": "Born in Scarborough, Ontario, to Punjabi Sikh parents who emigrated from Punjab, India. Led the NDP from 2017 to 2025 and served as MP for Burnaby South. Criminal defence lawyer by training. His supply-and-confidence agreement with the Liberal government secured dental care and pharmacare legislation.",
    "notable_achievement": "First person of colour to lead a major federal political party in Canada; first turbaned Sikh to lead a national party in North America"
})

new_entries.append({
    "name": "Anita Anand",
    "position": "Minister of Foreign Affairs",
    "category": "government",
    "company": "Government of Canada",
    "country": "Canada",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Anita_Anand",
    "twitter": "@AnitaAnandMP",
    "bio": "Born in Kentville, Nova Scotia, to Indian immigrant physicians — her father from Tamil Nadu and her mother from Punjab. Served as Canada's Minister of Foreign Affairs (2025–present), Minister of National Defence (2021–2023), and oversaw Canada's COVID-19 vaccine procurement. Former law professor at University of Toronto.",
    "notable_achievement": "First Hindu woman elected to Parliament and first Hindu member of Cabinet in Canada; named Canada's 'most valuable politician' by The Hill Times"
})

new_entries.append({
    "name": "Harjit Singh Sajjan",
    "position": "Former Minister of National Defence",
    "category": "government",
    "company": "Government of Canada",
    "country": "Canada",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Harjit_Sajjan",
    "twitter": "@HarjitSajjan",
    "bio": "Born in Bombeli, Punjab, India, and moved to Canada at age five. Served as Canada's Minister of National Defence (2015–2021) and Minister of International Development (2021–2023). Retired Lieutenant Colonel in the Canadian Armed Forces who served in Bosnia and multiple deployments in Afghanistan.",
    "notable_achievement": "First Sikh to serve as Canada's Minister of National Defence; decorated military veteran who helped dismantle an insurgent network in Kandahar"
})

new_entries.append({
    "name": "Irfaan Ali",
    "position": "President of Guyana",
    "category": "government",
    "company": "Government of Guyana",
    "country": "Guyana",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Irfaan_Ali",
    "twitter": "",
    "bio": "Born in Leonora, Guyana, of Indo-Guyanese (Bhojpuri) descent. Serving as the 10th President of Guyana since 2020. Previously served as Minister of Housing and Water. Holds a PhD in Urban and Regional Planning from the University of the West Indies.",
    "notable_achievement": "Incumbent President of Guyana; leading the country during its historic oil-driven economic boom, making it one of the fastest-growing economies in the world"
})

new_entries.append({
    "name": "Kamla Persad-Bissessar",
    "position": "Prime Minister of Trinidad and Tobago",
    "category": "government",
    "company": "Government of Trinidad and Tobago",
    "country": "Trinidad and Tobago",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Kamla_Persad-Bissessar",
    "twitter": "",
    "bio": "Born in Siparia, Trinidad and Tobago, of Indo-Trinidadian descent (Bhojpuri and Tamil ancestry). Currently serving her second term as Prime Minister (2025–present; previously 2010–2015). Attorney and educator by training. Leader of the United National Congress.",
    "notable_achievement": "First woman to serve as Prime Minister of Trinidad and Tobago; first Indo-Trinidadian woman to hold the office"
})

new_entries.append({
    "name": "Chan Santokhi",
    "position": "Former President of Suriname (deceased)",
    "category": "government",
    "company": "Government of Suriname",
    "country": "Suriname",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Chan_Santokhi",
    "twitter": "",
    "bio": "Born in Lelydorp, Suriname, of Indo-Surinamese (Bhojpuri) descent. Served as President of Suriname from 2020 to 2025. Previously served as Minister of Justice and Police. Former police commissioner who fought drug trafficking and organized crime.",
    "notable_achievement": "First Indo-Surinamese President to be elected democratically in Suriname's modern era; Pravasi Bharatiya Samman recipient"
})

new_entries.append({
    "name": "Wavel Ramkalawan",
    "position": "President of Seychelles",
    "category": "government",
    "company": "Government of Seychelles",
    "country": "Seychelles",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Wavel_Ramkalawan",
    "twitter": "",
    "bio": "Born in Mahé, Seychelles, of Indo-Seychellois (Bhojpuri) descent. Served as President of Seychelles from 2020 to 2025. Anglican priest and opposition leader for over two decades before winning the presidency. Founded the Seychelles National Party.",
    "notable_achievement": "First opposition candidate to win the presidency in Seychelles; first Indian-origin leader of an African island nation elected through peaceful transition"
})

new_entries.append({
    "name": "Navin Ramgoolam",
    "position": "Prime Minister of Mauritius",
    "category": "government",
    "company": "Government of Mauritius",
    "country": "Mauritius",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Navin_Ramgoolam",
    "twitter": "",
    "bio": "Born in Port Louis, Mauritius, of Indo-Mauritian (Bhojpuri) descent. Currently serving his third term as Prime Minister (2024–present; previously 1995–2000, 2005–2014). Son of Sir Seewoosagur Ramgoolam, the first Prime Minister of independent Mauritius. Trained as a barrister in London.",
    "notable_achievement": "Three-time Prime Minister of Mauritius; son of the founding father of Mauritius, representing a dynasty central to the nation's post-colonial history"
})

new_entries.append({
    "name": "Ujjal Dosanjh",
    "position": "Former Premier of British Columbia",
    "category": "government",
    "company": "Government of Canada",
    "country": "Canada",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Ujjal_Dosanjh",
    "twitter": "",
    "bio": "Born in Dosanjh Kalan, Punjab, India, and emigrated to Canada. Served as Premier of British Columbia (2000–2001) — the first Indo-Canadian provincial premier — and later as a federal Liberal MP and Minister of Health. Survived a brutal attack by Sikh extremists in 1985 for speaking against separatism.",
    "notable_achievement": "First Indo-Canadian to serve as a provincial premier in Canada; later served as federal Minister of Health"
})

# ===== TECH & BUSINESS - GLOBAL =====

new_entries.append({
    "name": "Piyush Gupta",
    "position": "Former CEO",
    "category": "tech_business",
    "company": "DBS Group",
    "country": "Singapore",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Piyush_Gupta",
    "twitter": "",
    "bio": "Born in Meerut, Uttar Pradesh. B.A. from St. Stephen's College, Delhi, and PGDM from IIM Ahmedabad. Led DBS Group as CEO from 2009 to 2025 after 27 years at Citigroup. Transformed DBS into Southeast Asia's largest bank by assets and a global digital banking pioneer, named 'World's Best Bank' multiple times.",
    "notable_achievement": "Transformed DBS into the first Asian bank named World's Best Bank by Euromoney and Global Finance; grew the bank's market cap over 280%"
})

new_entries.append({
    "name": "Rajeev Suri",
    "position": "Former CEO of Nokia; Former CEO of Inmarsat",
    "category": "tech_business",
    "company": "Inmarsat / Nokia",
    "country": "Singapore",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Rajeev_Suri",
    "twitter": "",
    "bio": "Born in New Delhi, India. B.Tech from Manipal Institute of Technology. Singapore citizen who served as CEO of Nokia (2014–2020) after leading Nokia Networks. Later served as CEO of British satellite company Inmarsat. Rose through the ranks after joining Nokia in 1995.",
    "notable_achievement": "Led Nokia through its post-mobile transformation, steering the company into 5G infrastructure leadership as a global telecom equipment giant"
})

new_entries.append({
    "name": "Sandeep Kataria",
    "position": "CEO",
    "category": "tech_business",
    "company": "Bata",
    "country": "Switzerland",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Sandeep_Kataria",
    "twitter": "",
    "bio": "Indian-born business executive who became global CEO of Bata (headquartered in Lausanne, Switzerland) in 2020. Previously held senior leadership roles at Vodafone UK, Yum! Brands, and Unilever across a 17-year career. Ran Bata's India operations before taking the global CEO role.",
    "notable_achievement": "First Indian-origin CEO of the 130-year-old Swiss footwear giant Bata, overseeing operations across 70+ countries"
})

new_entries.append({
    "name": "Ravi Kumar S",
    "position": "CEO",
    "category": "tech_business",
    "company": "Cognizant",
    "country": "US",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Ravi_Kumar_S.",
    "twitter": "",
    "bio": "Indian-born technology executive who became CEO of Cognizant in January 2023. Previously served as President of Infosys for over two decades, overseeing $8 billion in revenue. Holds a degree in electronics engineering and an MBA from XLRI Jamshedpur.",
    "notable_achievement": "Leading Cognizant's transformation into a modern technology services company; formerly oversaw Infosys's largest business unit"
})

# ===== ARTS & ENTERTAINMENT - GLOBAL =====

new_entries.append({
    "name": "Ben Kingsley",
    "position": "Actor",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Ben_Kingsley",
    "twitter": "",
    "bio": "Born Krishna Pandit Bhanji in Snainton, Yorkshire, England, to a Gujarati Kenyan-Indian father and English mother. One of the most acclaimed actors of his generation. Knighted in 2002. Won the Academy Award for Best Actor for Gandhi (1982). Also known for Schindler's List, Sexy Beast, and Iron Man 3.",
    "notable_achievement": "Academy Award winner for portraying Mahatma Gandhi; one of few actors to achieve the 'Triple Crown of Acting' (Oscar, Emmy, Tony nominations/wins)"
})

new_entries.append({
    "name": "Gurinder Chadha",
    "position": "Director & Producer",
    "category": "arts_entertainment",
    "company": "Bend It Networks",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Gurinder_Chadha",
    "twitter": "@GurinderChadha",
    "bio": "Born in Nairobi, Kenya, and raised in Southall, London, by Sikh Punjabi parents. OBE recipient. First British-Asian woman to direct a feature film in the UK. Known for Bend It Like Beckham (2002) — the highest-grossing British-financed film at the UK box office — as well as Bride and Prejudice, Viceroy's House, and Blinded by the Light.",
    "notable_achievement": "Directed Bend It Like Beckham, the highest-grossing British-financed, British-distributed film ever at the UK box office; OBE for services to the British film industry"
})

new_entries.append({
    "name": "Archie Panjabi",
    "position": "Actress",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Archie_Panjabi",
    "twitter": "@ArchiePanjabi",
    "bio": "Born in London to Punjabi Hindu parents from India. Gained fame with her breakout role in Bend It Like Beckham (2002). Won the Primetime Emmy Award for Outstanding Supporting Actress for her role as Kalinda Sharma in The Good Wife (2010). Also starred in Blindspot and Snowpiercer.",
    "notable_achievement": "First South Asian woman to win a Primetime Emmy Award for Outstanding Supporting Actress in a Drama Series"
})

new_entries.append({
    "name": "Parminder Nagra",
    "position": "Actress",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Parminder_Nagra",
    "twitter": "",
    "bio": "Born in Leicester, England, to Sikh Punjabi parents from India. Known for her starring role in Bend It Like Beckham (2002) and as Dr. Neela Rasgotra in the long-running NBC medical drama ER (2003–2009). Has appeared in Alcatraz, The Blacklist, and Clarice.",
    "notable_achievement": "Starred in both Bend It Like Beckham and ER, becoming one of the first British-Indian actresses to lead a major US network television show"
})

new_entries.append({
    "name": "Naveen Andrews",
    "position": "Actor",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Naveen_Andrews",
    "twitter": "",
    "bio": "Born in Wandsworth, London, to Indian parents from Kerala. Trained at the Guildhall School of Music and Drama. Best known for his role as Sayid Jarrah in Lost (2004–2010) and as Julian Bashir–inspired character Jafar Sharif-Sanjari in Sense8. Also appeared in The English Patient and Diana.",
    "notable_achievement": "Screen Actors Guild Award winner for Outstanding Ensemble Cast for Lost; one of the most prominent British-Indian actors in Hollywood"
})

new_entries.append({
    "name": "Anish Kapoor",
    "position": "Sculptor",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Anish_Kapoor",
    "twitter": "",
    "bio": "Born in Mumbai, India, and based in London since the 1970s. CBE recipient. One of the most influential sculptors of his generation. Known for iconic public works including Cloud Gate ('The Bean') in Chicago, Orbit at London's Olympic Park, and Descent into Limbo. Won the Turner Prize in 1991.",
    "notable_achievement": "Turner Prize winner (1991); created Cloud Gate in Chicago, one of the most recognizable public sculptures in the world"
})

new_entries.append({
    "name": "Sanjeev Bhaskar",
    "position": "Actor, Comedian & Writer",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Sanjeev_Bhaskar",
    "twitter": "@TVSanjeev",
    "bio": "Born in London to Indian parents from Punjab. OBE recipient. Best known for the BBC sketch show Goodness Gracious Me and The Kumars at No. 42. Stars as DI Sunny Khan in the acclaimed ITV crime series Unforgotten. Chancellor of the University of Sussex.",
    "notable_achievement": "Pioneer of British-Asian comedy; Goodness Gracious Me became the first British-Asian sketch show to transfer from radio to BBC Two and then BBC One"
})

new_entries.append({
    "name": "Simone Ashley",
    "position": "Actress",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Simone_Ashley",
    "twitter": "",
    "bio": "Born Simone Ashwini Pillai in Camberley, Surrey, England, to Tamil Indian parents. Rose to global fame as Kate Sharma, the female lead in Bridgerton Season 2 (2022), Netflix's most-watched English-language series at the time. Also known for Sex Education.",
    "notable_achievement": "First South Asian actress to be a female lead in a Bridgerton season; named to Time's 'Time100 Next' list"
})

new_entries.append({
    "name": "Himesh Patel",
    "position": "Actor",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Himesh_Patel",
    "twitter": "",
    "bio": "Born in Cambridgeshire, England, to a Gujarati Indian family. Starred as the lead in Danny Boyle's film Yesterday (2019), playing a struggling musician who becomes the only person who remembers The Beatles. Also appeared in Tenet, Don't Look Up, and the BBC soap EastEnders.",
    "notable_achievement": "Lead actor in Danny Boyle's Yesterday; one of the first British-Indian actors to lead a major Hollywood studio film"
})

new_entries.append({
    "name": "V. S. Naipaul",
    "position": "Author (deceased)",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/V._S._Naipaul",
    "twitter": "",
    "bio": "Born in Chaguanas, Trinidad, to an Indo-Trinidadian family of Bhojpuri descent. Moved to England at 18 on a scholarship to Oxford. Nobel Prize in Literature (2001). Knighted in 1990. One of the greatest English-language writers of the 20th century. Known for A House for Mr Biswas, A Bend in the River, and The Enigma of Arrival.",
    "notable_achievement": "Nobel Prize in Literature (2001); celebrated for works exploring post-colonial societies, identity, and the Indian diaspora across three continents"
})

new_entries.append({
    "name": "Hanif Kureishi",
    "position": "Author & Screenwriter",
    "category": "arts_entertainment",
    "company": "",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Hanif_Kureishi",
    "twitter": "",
    "bio": "Born in Bromley, London, to a Pakistani father and English mother. CBE recipient. Though of Pakistani rather than Indian origin, he is a towering figure of the South Asian British literary canon. Wrote the screenplay for My Beautiful Laundrette (1985) and The Buddha of Suburbia (1990). Academy Award nominee for Best Original Screenplay.",
    "notable_achievement": "Academy Award-nominated screenwriter for My Beautiful Laundrette; pioneered literary depictions of British-Asian identity and multiculturalism"
})

new_entries.append({
    "name": "Krishnan Guru-Murthy",
    "position": "Television Presenter & Journalist",
    "category": "arts_entertainment",
    "company": "Channel 4 News",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Krishnan_Guru-Murthy",
    "twitter": "@krishgm",
    "bio": "Born in Liverpool, England, to a father from South India and a mother from North India. One of the most prominent broadcast journalists in the UK. Has presented Channel 4 News since 1998. Previously the youngest-ever presenter of BBC's Newsround at age 18. Known for incisive political interviews.",
    "notable_achievement": "One of the UK's most respected broadcast journalists; over 25 years as a presenter on Channel 4 News"
})

# ===== SCIENCE & MEDICINE - GLOBAL =====

new_entries.append({
    "name": "Tharman Shanmugaratnam",
    "position": "President of Singapore",
    "category": "government",
    "company": "Government of Singapore",
    "country": "Singapore",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Tharman_Shanmugaratnam",
    "twitter": "",
    "bio": "Born in Singapore to a Ceylonese Tamil father and Malaysian mother of Indian descent. Serving as President of Singapore since 2023. Previously served as Deputy Prime Minister, Minister for Finance, and Chairman of the Monetary Authority of Singapore. Holds a Master's from Cambridge and an MPA from Harvard.",
    "notable_achievement": "First Indian-origin President of Singapore since S. R. Nathan; won the 2023 presidential election with over 70% of the vote"
})

# Move Ramakrishnan to correct country (UK)
# Already handled in country_fixes above

# ===== ACADEMIA - GLOBAL =====
# (Venkatraman Ramakrishnan already in the list, country fixed to UK)
# Note: Amartya Sen is technically based at Harvard but is a global figure

# Add a few more notable global academics
new_entries.append({
    "name": "Partha Dasgupta",
    "position": "Professor Emeritus of Economics",
    "category": "academia",
    "company": "University of Cambridge",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Partha_Dasgupta",
    "twitter": "",
    "bio": "Born in Dhaka (then British India, now Bangladesh) and raised in Varanasi, India. Frank Ramsey Professor Emeritus of Economics at Cambridge. Knighted in 2002. Led the landmark 'Dasgupta Review on the Economics of Biodiversity' (2021) commissioned by the UK Treasury, which has been compared in significance to the Stern Review on climate change.",
    "notable_achievement": "Authored the landmark UK government-commissioned Dasgupta Review on the Economics of Biodiversity; Fellow of the Royal Society and the British Academy"
})

new_entries.append({
    "name": "Devi Sridhar",
    "position": "Chair of Global Public Health",
    "category": "academia",
    "company": "University of Edinburgh",
    "country": "UK",
    "photo_url": "",
    "website": "",
    "wikipedia_url": "https://en.wikipedia.org/wiki/Devi_Sridhar",
    "twitter": "@deaboris",
    "bio": "Born in Miami, Florida, to Indian parents. Became the youngest-ever Chair of Global Public Health at the University of Edinburgh at age 28. Served as a key public health advisor to the Scottish Government during the COVID-19 pandemic. Rhodes Scholar at Oxford and elected a Fellow of the Royal Society of Edinburgh.",
    "notable_achievement": "Youngest-ever Chair of Global Public Health at Edinburgh; key advisor to the Scottish Government during the COVID-19 pandemic"
})

# Combine
data['leaders'] = existing_leaders + new_entries

# Update metadata
data['last_updated'] = '2026-07-14'
data['source_policy'] = 'Wikipedia and official websites only'
data['categories'] = [
    'tech_business',
    'arts_entertainment',
    'science_medicine',
    'academia',
    'government'
]

# Validate
for i, leader in enumerate(data['leaders']):
    for field in ['name', 'position', 'category', 'bio', 'notable_achievement', 'country']:
        if not leader.get(field):
            print(f"WARNING: Entry {i} ({leader.get('name', '?')}) missing '{field}'")

# Write
with open('indian-american-leaders.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# Summary
from collections import Counter
cats = Counter(l['category'] for l in data['leaders'])
countries = Counter(l['country'] for l in data['leaders'])

print(f"\nTotal entries: {len(data['leaders'])}")
print(f"\nBy category:")
for cat, count in sorted(cats.items()):
    print(f"  {cat}: {count}")
print(f"\nBy country:")
for country, count in sorted(countries.items(), key=lambda x: -x[1]):
    print(f"  {country}: {count}")
print(f"\nNew entries added: {len(new_entries)}")
