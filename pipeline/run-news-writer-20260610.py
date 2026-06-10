#!/usr/bin/env python3
"""
Videshi News Writer — June 10, 2026 batch
3 articles: G-Sec tax exemption NRIs, SEBI bond tokenisation, Belfast riots diaspora angle
"""

import os, json, requests, uuid
from datetime import datetime, timezone

# Load env
env_path = os.path.expanduser("~/.env.supabase")
with open(env_path) as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, _, val = line.partition("=")
            key = key.replace("export ", "").strip()
            val = val.strip().strip('"').strip("'")
            os.environ[key] = val

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation"
}

def insert_article(article):
    """Insert article into p2_articles."""
    r = requests.post(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS,
        json=article,
        timeout=30
    )
    if r.status_code in (200, 201):
        data = r.json()
        if isinstance(data, list) and data:
            print(f"  ✓ Inserted: {data[0].get('slug', 'unknown')}")
            return data[0]
        print(f"  ✓ Inserted (no data returned)")
        return data
    else:
        print(f"  ✗ Failed ({r.status_code}): {r.text[:200]}")
        return None

now_utc = datetime.now(timezone.utc).isoformat()

# ============================================================
# ARTICLE 1: India's G-Sec Tax Exemption Leaves NRIs Out
# ============================================================

article1_body = """India's decision to scrap all taxes on foreign institutional investments in government securities is the most aggressive bid for overseas capital the country has made in over a decade. But for the millions of individual NRIs who park money in India through bank deposits and mutual funds, the new rules do not apply.

The Income-tax (Amendment) Ordinance, 2026, promulgated on June 5, inserts two new exemptions into Schedule IV of the Income-tax Act. Entry 13D exempts Foreign Institutional Investors from paying any tax — income tax on interest or capital gains — on government securities. Entry 13E extends the same benefit to the Bank for International Settlements. Both exemptions are retroactive to April 1, 2026.

The policy context is unmistakable. India's forex reserves have fallen roughly $46 billion in three months, from $728 billion to $682 billion. The rupee has weakened more than 5% since January, hammered by elevated oil prices from the Iran war and a record $28 billion in foreign equity outflows. The RBI kept the repo rate unchanged at 5.25% last week but simultaneously announced a raft of measures — concessional forex swaps, expanded Fully Accessible Route securities, removal of sub-limits on FPI bond investments — all aimed at pulling dollars back into the system.

## The NRI Gap

The ordinance's fine print, however, makes clear that these exemptions apply only to Foreign Portfolio Investors — typically hedge funds, pension funds, sovereign wealth funds, and other institutional pools registered with SEBI. Retail NRI investors who hold government bonds directly, or through NRE and NRO accounts, remain subject to the existing tax regime: a 20% withholding tax on interest earned and a 12.5% long-term capital gains tax on bonds held over 12 months.

"The Government's immediate focus appears to attract institutional portfolio flows rather than retail or individual overseas investors," said Amarjeet Singh Arora, partner at BDO India's financial services advisory practice. "There may be some case for extending similar benefits to NRIs, who are equally contributing foreign capital to India."

The gap is not merely symbolic. NRI deposits in Indian banks stood at roughly $150 billion as of March 2026, a significant source of stable forex. Industry bodies including FICCI and the NRI Commission have already signalled they will push for the exemption to be extended.

## A Workaround Exists — But It Is Not Simple

Nehal Sampat, a partner at Price Waterhouse & Co LLP, pointed out that NRIs can technically access the new tax exemption — but only through a circuitous route. "NRIs can benefit from tax exemption announced for interest and capital gains from Government securities for FPIs by investing in offshore funds and GIFT IFSC Funds registered as FPIs," he said.

In practice, this means setting up or investing through a GIFT City-domiciled fund that is SEBI-registered as an FPI, then having that fund buy government bonds on their behalf. The compliance and cost overhead makes this practical only for high-net-worth individuals, not the diaspora doctor or engineer parking savings in India.

## What Comes Next

The RBI has separately expanded the Fully Accessible Route to include 15-, 30-, and 40-year government bonds and Sovereign Green Bonds. It has also merged the "general" and "long-term" FPI sub-categories into a single investment limit and removed concentration caps. Jefferies estimates the combined measures could attract $50 billion to $70 billion in foreign inflows over the next 12 months.

For NRIs watching from the US, UK, and Gulf, the message is mixed. India is desperate enough for capital to rewrite its tax code by ordinance — a route that bypasses parliamentary debate entirely. The institutions are being courted with red carpets. Individual NRIs, for now, are being asked to wait in line.

*Sources: Income-tax (Amendment) Ordinance, 2026; Reserve Bank of India circular (June 5, 2026); Reuters; The Hindu Business Line; CA Club India*"""

article1 = {
    "headline": "India Just Made Government Bonds Tax-Free for Foreign Funds. NRIs Were Not Invited.",
    "subheadline": "The June 5 ordinance exempts institutional investors from all taxes on G-Secs. Individual diaspora investors still pay 20% withholding and 12.5% capital gains.",
    "body": article1_body,
    "slug": "india-gsec-tax-free-fpi-nri-excluded-ordinance-june-2026-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a3/Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg/1280px-Tower_and_building_of_Reserve_Bank_of_India%2C_Mumbai_02.jpg",
    "image_caption": "The Reserve Bank of India headquarters in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        "Income-tax (Amendment) Ordinance, 2026",
        "Reserve Bank of India circular (June 5, 2026)",
        "Reuters",
        "The Hindu Business Line",
        "CA Club India"
    ]),
    "published_at": now_utc
}

# ============================================================
# ARTICLE 2: SEBI Plans Bond Tokenisation Pilot
# ============================================================

article2_body = """India's markets regulator wants to put bonds on a blockchain. SEBI Chairman Tuhin Kanta Pandey said on Monday that the Securities and Exchange Board of India will launch a bond tokenisation pilot within six to nine months — a move that could fundamentally change how India's ₹9 lakh crore corporate bond market works.

Speaking at the ICICI Securities India Investor Conference in Mumbai, Pandey outlined a reform agenda that goes well beyond the pilot. SEBI and the Reserve Bank of India are jointly developing derivatives on corporate bond indices. A market-making framework to improve secondary bond liquidity is being designed. And the electronic book provider platform has already been expanded to cover issuances by REITs and InvITs.

## What Bond Tokenisation Actually Means

Tokenisation converts a bond — a financial instrument that represents a loan to a company or government — into a digital token on a blockchain. Each token represents a fraction of the bond's face value, making it possible to trade smaller units than traditional markets allow.

The practical impact could be significant. India's corporate bond market has grown rapidly — issuances have crossed ₹9 lakh crore, overall market capitalisation sits at roughly 128% of GDP, and mutual fund assets have surpassed ₹80 lakh crore. But liquidity in the secondary bond market remains notoriously shallow. Most bonds are bought and held to maturity, and price discovery is poor.

Tokenisation addresses this by making bonds more divisible, more transferable, and potentially tradable 24/7 on blockchain-based platforms. It also opens the door to fractional ownership — a ₹10 lakh bond could theoretically be broken into ₹1,000 tokens, giving retail investors access to instruments that have historically been the preserve of institutions.

## The RBI Connection

SEBI is not working alone. The Reserve Bank of India released draft guidelines on total return swaps and corporate bond derivatives earlier this year, and Pandey confirmed those products will move forward once the regulatory framework is finalised. "RBI is in the process of finalising these guidelines, following which the exchanges will be launching these derivative products on bond indices," he said.

The coordination matters. India's bond market is split between government securities (regulated by RBI) and corporate bonds (regulated by SEBI). Any reform that touches both sides requires the two regulators to move in lockstep. The current push suggests they are doing exactly that.

## Why It Matters for NRIs

For overseas Indians looking at Indian debt markets, the timing is notable. The government scrapped capital gains and interest taxes on FPI investments in government securities just days ago. The RBI has expanded the Fully Accessible Route. And now SEBI is signalling that the plumbing of the bond market itself is about to be modernised.

India is also reviewing variable net worth requirements for stock brokers, though Pandey said no final decision has been taken. Taken together, the signals point to a regulator that sees capital markets as the primary channel for household savings and wealth creation — and wants the infrastructure to match that ambition.

## A Pilot, Not a Promise

Bond tokenisation is not new globally. Singapore, Switzerland, and Hong Kong have all run pilots. The European Investment Bank issued a digital bond on the Ethereum blockchain in 2021. But India's market is vastly larger in terms of retail participation, and the regulatory architecture — with SEBI, RBI, depositories, and exchanges all involved — is more complex.

A pilot within six to nine months means a working prototype is expected by early 2027. Whether it leads to full-scale adoption will depend on how well the technology performs in India's specific market conditions: settlement cycles, KYC requirements, and the appetite of mutual funds and insurance companies to participate.

For now, the direction is clear. India's capital markets regulator wants to bring the bond market into the blockchain era. The details will determine whether it actually gets there.

*Sources: SEBI Chairman Tuhin Kanta Pandey at ICICI Securities India Investor Conference (June 8, 2026); IANS; LiveMint; DevDiscourse*"""

article2 = {
    "headline": "SEBI Wants to Put India's Bonds on a Blockchain. A Pilot Is Coming Within Nine Months.",
    "subheadline": "The regulator plans to tokenise corporate bonds, launch derivatives on bond indices, and overhaul secondary market liquidity — all while coordinating with the RBI.",
    "body": article2_body,
    "slug": "sebi-bond-tokenisation-pilot-blockchain-india-capital-markets-reform-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cc/SEBI_Bhavan.jpg/1280px-SEBI_Bhavan.jpg",
    "image_caption": "SEBI Bhavan, the headquarters of the Securities and Exchange Board of India in Mumbai",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        "SEBI Chairman Tuhin Kanta Pandey (ICICI Securities India Investor Conference, June 8, 2026)",
        "IANS",
        "LiveMint",
        "DevDiscourse"
    ]),
    "published_at": now_utc
}

# ============================================================
# ARTICLE 3: Belfast Burns — Indian Diaspora in UK
# ============================================================

article3_body = """Masked men torched homes, burned a public bus, and smashed their way into houses across Belfast on Tuesday night in the worst anti-immigrant violence Northern Ireland has seen in over a year. For the estimated 1.8 million people of Indian origin living in Britain, the eruption is the latest in a string of incidents that have made the question of belonging feel increasingly urgent.

The riots followed a knife attack in north Belfast on Monday evening, in which a 30-year-old Sudanese national allegedly attempted to behead a man in his 40s. The victim survived, suffering severe injuries to his eyes, face, and back. The suspect was charged with attempted murder on Tuesday. Within hours, videos of the attack had gone viral, and organised groups of masked men began converging on streets across Belfast.

## The Violence

The BBC reported crowds of up to 300 people marching through Belfast, many with faces covered. A Glider bus was set ablaze with burning bins pushed inside it. Cars were torched in multiple neighbourhoods. In east Belfast, a crowd of approximately 100 men kicked in doors and smashed windows of homes, reportedly targeting migrant households.

"They're getting put out just because they're Black," Pastor Jack McKee told the BBC after attacks on homes in the north of the city.

Northern Ireland's First Minister Michelle O'Neill called the scenes "outright thuggery," adding that "groups of masked men burning families out of their homes is nothing less than disgusting cowardice." British Prime Minister Keir Starmer described the initial knife attack as "sickening" and said he had "absolutely no tolerance for abhorrent scenes of violence like this on our streets."

## The Broader Pattern

The Belfast violence does not exist in isolation. It follows the murder of university student Henry Nowak, an incident in which the killer — a Sikh man — falsely alleged a racial attack as Nowak lay dying, handcuffed by police. That case inflamed tensions around race and policing. Populist parties have seized on both incidents to attack the government's asylum and immigration policies.

Elon Musk weighed in, reposting messages from anti-immigrant activist Tommy Robinson and writing: "Only by protesting REPEATEDLY and LOUDLY will there be any change!!" Northern Ireland's Justice Minister Naomi Long responded that "bad faith actors" who would have previously struggled to find the province on a map were attempting to "weaponise the genuine hurt, concern and anger that people are feeling."

Claire Hanna, leader of the opposition SDLP in Northern Ireland, described what was unfolding as "a race-based pogrom."

## What This Means for the Indian Diaspora

Britain is home to the third-largest Indian diaspora in the world, after the US and the Gulf states. According to the 2021 census, 1.86 million people of Indian ethnicity live in England and Wales alone, with significant communities in Leicester, Birmingham, London, and across Northern Ireland and Scotland.

The community has not been directly targeted in the Belfast riots, which appear to have focused on Black and Middle Eastern residents. But the climate of hostility toward immigrants and visible minorities in Britain has grown markedly over the past two years, and Indian community organisations have expressed concern.

Last year, Northern Ireland experienced a similar wave of anti-immigrant rioting after an alleged sexual assault. Charges in that case were later withdrawn. In 2024, riots erupted across England after the Southport stabbing, with mosques and asylum seeker housing targeted in towns across the country.

For NRIs in Britain — many of whom hold British citizenship and have lived in the country for decades — the pattern raises fundamental questions about whether the social contract they signed up for still holds. The violence in Belfast is a Northern Irish story, shaped by the region's particular history with sectarian conflict. But the fuel feeding it — viral videos, algorithmic amplification, organised far-right mobilisation, and a political class struggling to hold the centre — is nationwide.

## What Happens Next

The suspect in the Belfast stabbing is due to appear at Belfast Magistrates' Court on Wednesday. Police have appealed for calm but acknowledged "sporadic pockets of disorder" across Northern Ireland. All bus and train services in Belfast were suspended on Tuesday night.

Smaller protests were also reported in Bangor, Glasgow, and outside Parliament in London. Whether the violence spreads further or subsides will depend in large part on whether political leaders can regain control of the narrative — and whether social media platforms take action against the accounts amplifying calls for more protests.

For the Indian community in Britain, the message is sobering. Integration, professional success, and decades of community building do not insulate anyone from a moment when the mood turns and the distinction between "immigrant" and "citizen" starts to blur.

*Sources: Reuters; CNN; BBC; The Times; New York Post; 2021 UK Census*"""

article3 = {
    "headline": "Belfast Is Burning After a Knife Attack. Britain's 1.8 Million Indians Are Watching Closely.",
    "subheadline": "Masked mobs torched homes and buses across Northern Ireland in the worst anti-immigrant violence in over a year. The Indian diaspora in the UK faces a growing climate of hostility.",
    "body": article3_body,
    "slug": "belfast-anti-immigrant-riots-indian-diaspora-uk-knife-attack-20260610",
    "category": "news",
    "status": "review",
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Custom_House%2C_River_Lagan%2C_Belfast.jpg/1280px-Custom_House%2C_River_Lagan%2C_Belfast.jpg",
    "image_caption": "Belfast's Custom House on the River Lagan, the city now gripped by anti-immigrant violence",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps([
        "Reuters",
        "CNN",
        "BBC",
        "The Times",
        "New York Post",
        "2021 UK Census"
    ]),
    "published_at": now_utc
}

# ============================================================
# INSERT ALL ARTICLES
# ============================================================

articles = [article1, article2, article3]

print(f"\n{'='*60}")
print(f"Videshi News Writer — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Inserting {len(articles)} articles...")
print(f"{'='*60}\n")

success = 0
for i, article in enumerate(articles, 1):
    print(f"[{i}/{len(articles)}] {article['headline'][:70]}...")
    result = insert_article(article)
    if result:
        success += 1
    print()

print(f"{'='*60}")
print(f"Done. {success}/{len(articles)} articles inserted successfully.")
print(f"{'='*60}")
