#!/usr/bin/env python3
"""News writer for The Videshi - June 5, 2026 batch"""
import json, os, subprocess, uuid, datetime

# Load env
def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                if line.startswith('export '):
                    line = line[7:]
                k, v = line.split('=', 1)
                v = v.strip('"').strip("'")
                os.environ[k] = v

load_env('~/.env.supabase')
SUPABASE_URL = os.environ['SUPABASE_URL']
SUPABASE_KEY = os.environ['SUPABASE_SERVICE_ROLE_KEY']

def insert_article(article):
    """Insert article into Supabase p2_articles table"""
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation'
    }
    
    payload = json.dumps(article)
    cmd = [
        'curl', '-sS', '-X', 'POST',
        f'{SUPABASE_URL}/rest/v1/p2_articles',
        '-H', f'apikey: {SUPABASE_KEY}',
        '-H', f'Authorization: Bearer {SUPABASE_KEY}',
        '-H', 'Content-Type: application/json',
        '-H', 'Prefer: return=representation',
        '-d', payload
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        print(f"  ✗ curl error: {result.stderr}")
        return False
    
    try:
        resp = json.loads(result.stdout)
        if isinstance(resp, list) and len(resp) > 0:
            print(f"  ✓ Inserted: {resp[0].get('slug', 'unknown')}")
            return True
        elif isinstance(resp, dict) and 'message' in resp:
            print(f"  ✗ Error: {resp['message']}")
            return False
        else:
            print(f"  ? Response: {result.stdout[:200]}")
            return False
    except json.JSONDecodeError:
        print(f"  ✗ JSON decode error: {result.stdout[:200]}")
        return False

now = datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

# =====================================================
# ARTICLE 1: US-Iran Ceasefire Deal / Hormuz Reopening
# =====================================================
article1 = {
    "headline": "The US and Iran Are One Signature Away From Reopening the Strait of Hormuz. India Cannot Afford a Collapse.",
    "subheadline": "Negotiators have agreed on terms that would extend the ceasefire by 60 days and unblock the world's most important oil chokepoint. Trump has not yet signed.",
    "slug": "us-iran-ceasefire-deal-hormuz-reopen-india-oil-prices-june-2026",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/16/Strait_of_Hormuz_and_Musandam_Peninsula_%28MODIS_2018-12-10%29.jpg",
    "image_caption": "Satellite image of the Strait of Hormuz, the maritime chokepoint at the center of US-Iran ceasefire talks",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps(["Reuters", "NBC News", "Wall Street Journal", "Madhyam Online"]),
    "body": """Four months into a war that has upended global energy markets, the United States and Iran appear to be closer to a ceasefire extension than at any point since hostilities began. Negotiators from both sides have reached an agreement in principle, according to a senior Arab official directly involved in the talks. The deal, however, is still waiting on final approval from President Donald Trump and Iran's top leadership.

The proposed terms are straightforward in concept and enormous in consequence. The Strait of Hormuz — through which roughly 20 percent of the world's oil supply normally flows — would reopen to commercial shipping. The ceasefire, already in a fragile state after exchanges of fire earlier this week, would be formally extended by 60 days. That window would be used to negotiate the far harder question: Iran's nuclear program.

## What the Deal Contains

The framework, details of which were released by Iranian media, centers on three pillars. First, the immediate reopening of the Strait of Hormuz, which has been effectively closed to major shipping traffic since February. Second, a 60-day diplomatic runway for nuclear talks, during which both sides would refrain from offensive military operations. Third, an implicit understanding that sanctions relief — Iran's most urgent demand — will not be on the table until Trump's core conditions are met.

Secretary of State Marco Rubio made those conditions explicit on Friday. "The strait needs to be open, unimpeded, without tolls, and obviously that needs to happen immediately," he said. Treasury Secretary Scott Bessent reinforced the sequencing: "Open the Strait, highly enriched uranium, no nuclear program."

Iran, for its part, has pushed to maintain some form of control over traffic through the strait indefinitely. Iranian Deputy Foreign Minister Kazem Gharibabadi told Iranian media on June 4 that Tehran still demands the immediate release of at least half of its frozen assets upon signing any memorandum of understanding. The gap between what each side considers non-negotiable has been the central obstacle for weeks.

## Why This Week Was Different

The pace of events over the past 72 hours has been unlike anything since the ceasefire was first announced in April. On Wednesday, Trump told reporters at the White House that the strait would reopen "immediately" upon signing and that US forces had already deployed minesweeping equipment and cleared most suspected mines. On Thursday, he went further, saying Washington did not need a deal to secure Iran's enriched uranium — a statement that could be read as either leverage or a signal that the nuclear dimension might be deferred.

On Friday, the US carried out new strikes in southern Iran, hitting military targets near the strait. The Pentagon described them as defensive. Iran warned it would "respond decisively to any violation of the ceasefire." Yet both sides continued talking.

Vice President JD Vance acknowledged that language points were still being worked out but expressed cautious optimism. "We're going back and forth on a couple of language points," Vance said. "I do think we've made a lot of progress here."

## What It Means for India

For India, the stakes are existential in economic terms. The near-total closure of Hormuz stranded more than 13 million barrels of oil per day within the Gulf, forcing India to scramble for alternative suppliers in Latin America and Africa. The rupee has fallen nearly 5 percent to historic lows since the conflict began. Brent crude has hovered near $100 a barrel, and India's fuel import bill — already around $120 billion annually — has ballooned further.

On Friday, the Reserve Bank of India held its policy rate steady at 5.25 percent and announced a raft of measures to attract dollar inflows, including scrapping capital gains tax for foreign holders of government bonds and sweetening deposit schemes for non-resident Indians. The RBI raised its inflation projection for the fiscal year to 5.1 percent from 4.6 percent and trimmed its GDP growth forecast to 6.6 percent from 6.9 percent.

Market reaction to the possibility of a deal has been swift. When Trump announced Saturday that an agreement was "largely negotiated," Brent crude fell nearly $15 to around $99 a barrel. But the volatility cuts both ways. If talks collapse — and they have before — prices could spike past the levels that preceded the ceasefire.

## The Complication No One Is Talking About

Trump added a condition on Saturday that was not part of the original framework: he wants more Middle Eastern countries to sign onto the Abraham Accords, the normalization agreement with Israel that he brokered during his first term. Whether Iran would accept a deal that explicitly links the Hormuz reopening to expanded Israeli normalization is unclear. Iran's Foreign Ministry has previously stated that any violation on one front constitutes a violation on all fronts.

The next 48 to 72 hours will determine whether four months of economic pain, shipping chaos, and diplomatic brinkmanship produce a tangible result — or whether the world's most important oil chokepoint remains closed into the summer.

For the millions of Indians who have watched fuel prices climb, the rupee weaken, and inflation forecasts rise, the answer cannot come soon enough."""
}

print("Article 1: US-Iran deal / Hormuz")
insert_article(article1)
print()

# =====================================================
# ARTICLE 2: India Flex-Fuel / Ethanol Station Rollout
# =====================================================
article2 = {
    "headline": "India Just Launched Its First Flex-Fuel Car. Five Thousand Ethanol Pumps Will Follow by 2027.",
    "subheadline": "Maruti Suzuki's WagonR now runs on 100 percent ethanol. The government plans 500 stations this year and 5,000 by December 2027 to cut a $120 billion fuel import bill.",
    "slug": "india-flex-fuel-maruti-wagonr-ethanol-stations-puri-2026",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/4d/Hardeep_Singh_Puri_with_PM_Modi_%28cropped%29.jpg",
    "image_caption": "Petroleum Minister Hardeep Singh Puri, who announced India's flex-fuel station rollout alongside Prime Minister Modi",
    "image_attribution": "Wikimedia Commons",
    "sources": json.dumps(["The Hindu BusinessLine", "Devdiscourse", "Energy Watch", "Impressive Times"]),
    "body": """India's flex-fuel future arrived on a Thursday afternoon in New Delhi, wrapped in the body of the country's most ubiquitous car. Maruti Suzuki — the automaker that put India on wheels — launched a flex-fuel variant of its WagonR that can run on E85 or E100 ethanol blends. One day earlier, Hero MotoCorp had rolled out flex-fuel versions of its Splendor and HF Deluxe motorcycles. Together, the two launches mark the moment India's two largest vehicle manufacturers committed to a fuel the country can grow in its own fields.

Petroleum and Natural Gas Minister Hardeep Singh Puri, speaking at the WagonR launch, outlined the infrastructure that will follow. The government will begin with 50 to 100 ethanol dispensing stations in Delhi-NCR, Mumbai, Pune, and Nagpur. That number is expected to reach 500 by the end of 2026 and 5,000 by December 2027.

## The Chicken-and-Egg Problem Is Over

Puri acknowledged that India had tried this before and failed. "Earlier, there was an attempt to set up a large number of dispensing stations, but the vehicle models were not ready," he said. "It was a little like the chicken-and-egg story."

The difference now is that both sides of the equation are moving simultaneously. Maruti Suzuki and Hero MotoCorp are selling vehicles that can burn high-ethanol blends. The government is building the retail network to fuel them. And India's ethanol production capacity has expanded nearly fivefold since 2014, from 421 crore litres to approximately 2,000 crore litres today.

The numbers behind the blending program are striking. Ethanol blending in petrol has risen from less than 1.5 percent in 2013-14 to 20 percent in the current fiscal year — hitting the national target five years ahead of schedule. Ethanol procurement has surged from around 38 crore litres in 2013-14 to over 1,040 crore litres. India can now produce ethanol from multiple feedstocks, including agricultural waste, grains, bamboo, and seaweed.

## The Economic Case

India's annual fossil fuel import bill stands at approximately $120 billion. In the context of the ongoing Hormuz crisis, which has disrupted oil shipments and driven crude prices near $100 a barrel, the urgency of reducing that dependence has sharpened considerably.

Puri estimated that if 50 percent of newly sold two-wheelers and four-wheelers become flex-fuel compatible, the shift would generate additional demand for over 311 crore litres of ethanol, provide nearly ₹12,403 crore in extra income for Indian farmers, and cut carbon dioxide emissions by approximately 66.4 lakh metric tonnes.

The government is planning a suite of supporting measures to accelerate adoption: pricing incentives, road tax concessions for flex-fuel vehicles, special identifiers for FFVs and their retail outlets, consumer awareness campaigns, and the development of storage and dispensing infrastructure.

## What the Diaspora Should Watch

For NRIs in the auto industry, the clean energy space, or agricultural supply chains, the flex-fuel push creates tangible opportunities. India is building a nationwide ecosystem from scratch — one that connects farmers growing feedstock to refineries producing ethanol to retail outlets dispensing it to vehicles engineered to burn it. Each link in that chain needs investment, technology, and expertise.

The move also has implications for India's carbon commitments. The Ministry of Petroleum has classified vehicles running on high ethanol blends such as E85 as zero-emission vehicles, noting that E85 fuel produces near-zero particulate matter. That classification could open doors to international green finance and carbon credit markets.

## What Comes Next

The flex-fuel WagonR will initially be available in select markets where E85 dispensing stations are operational. The government has indicated that pricing for ethanol-based fuel will be competitive with petrol, though the exact pricing framework has not been finalized.

The real test is not the launch but the scale. India has 400 million vehicles on its roads. Converting even a fraction of that fleet to flex-fuel will require thousands of dispensing stations, millions of compatible vehicles, and a feedstock supply chain that can reliably produce billions of litres of ethanol year after year.

Puri framed it in terms that went beyond fuel policy. "This is not merely a transition in fuel," he said. "It is the creation of a complete ecosystem for cleaner mobility, stronger energy security, and greater self-reliance."

India has set ambitious energy targets before and missed them. But the convergence of vehicle availability, production capacity, infrastructure funding, and geopolitical urgency suggests this time may be different. The WagonR — humble, practical, and everywhere — is an apt vehicle for the experiment."""
}

print("Article 2: Flex-fuel / ethanol")
insert_article(article2)
print()

# =====================================================
# ARTICLE 3: H-1B $100K Fee / 200K+ Applicants
# =====================================================
article3 = {
    "headline": "More Than 200,000 H-1B Applicants Paid $100,000 Each to Skip the Line. The System Has Never Seen Demand Like This.",
    "subheadline": "DHS Secretary Markwayne Mullin told Congress that 286,000 H-1B applications have been filed in FY2026 — and more than 70 percent opted for the premium route.",
    "slug": "h1b-visa-100000-fee-200000-applicants-dhs-mullin-congress-fy2026",
    "category": "news",
    "vertical": "news",
    "status": "published",
    "published_at": now,
    "is_editorial": False,
    "image_url": "https://images.pexels.com/photos/36984942/pexels-photo-36984942.jpeg?auto=compress&cs=tinysrgb&h=650&w=940",
    "image_caption": "US Immigration and Customs Enforcement building in Washington, DC",
    "image_attribution": "Pexels",
    "sources": json.dumps(["AviationA2Z", "Daily Caller", "Greenberg Traurig Immigration", "DHS Congressional Testimony"]),
    "body": """The number is difficult to absorb on first read: more than 200,000 people paid $100,000 each for the privilege of having their H-1B visa applications processed faster. That is $20 billion in fees alone, collected by the US government in a single fiscal year, from applicants so desperate to work in the United States that they — or their employers — were willing to pay a sum that exceeds the annual salary of many of the positions being filled.

Department of Homeland Security Secretary Markwayne Mullin disclosed the figure during testimony before the Senate Appropriations Subcommittee on Homeland Security. According to Mullin, the DHS has received approximately 286,000 H-1B applications so far in fiscal year 2026. More than 70 percent of those applicants — over 200,000 — opted for the premium processing route, paying the $100,000 fee that Trump signed into law via executive proclamation in September 2025.

## The Math Behind the Rush

The incentive is simple arithmetic. Standard H-1B processing takes approximately seven and a half months. Premium processing, at the $100,000 price point, takes about 15 days. For employers building teams around critical hires, or for workers whose immigration status hangs on the timing of an approval, the difference between two weeks and eight months is not a luxury — it is the difference between keeping a job and losing legal status.

The $100,000 fee was introduced as part of Trump's broader recalibration of the immigration system. When he signed the proclamation in September 2025, critics warned it would price out smaller employers and turn the visa into a tool exclusively for large corporations. Supporters argued it would filter for high-value applicants and generate revenue for enforcement.

The FY2026 data suggests both sides were partly right. Demand has not collapsed. If anything, it has intensified. But the concentration of applicants willing to pay that fee is overwhelmingly skewed toward large technology companies, consulting firms, and healthcare systems with the balance sheets to absorb the cost.

## What It Means for Indian Workers

Indians have historically accounted for roughly 74 percent of all H-1B visas issued — a figure that has held remarkably steady across administrations and policy shifts. If the same proportion holds for FY2026, approximately 212,000 of the 286,000 applications are likely from Indian nationals or their employers.

The $100,000 fee does not eliminate the annual cap or the lottery. It accelerates processing for those selected. But the sheer volume of premium applicants suggests that the system's bottleneck has moved from selection to processing speed — and that employers consider the cost of waiting far higher than the cost of the fee.

This comes against the backdrop of Congressman Chip Roy's American White-Collar Worker Jobs Act, introduced this week, which would end the H-1B lottery entirely and replace it with a merit-based selection system. Roy's bill would also require employers to pay H-1B holders the same wage as American workers with equivalent experience and qualifications, and mandate a Department of Labor market test to verify that a good-faith effort was made to hire domestically before sponsoring a foreign worker.

## The Two-Track System

What is emerging is a two-track H-1B system. On one track, applicants with deep-pocketed sponsors pay $100,000 and receive decisions in two weeks. On the other, those who cannot afford the fee wait more than seven months — a period during which they may be unable to change employers, travel, or plan their lives with any certainty.

For Indian tech workers, many of whom are already navigating decade-long green card backlogs, the fee adds another layer of financial pressure to a system that was already testing their patience. A software engineer at a mid-size firm whose employer will not cover the $100,000 fee faces a fundamentally different immigration experience than one at a Fortune 500 company that considers it a routine cost of doing business.

## The Revenue Question

If 200,000 applicants have paid $100,000 each, the US government has collected approximately $20 billion from H-1B premium processing alone in FY2026. That figure dwarfs the entire annual budget of US Citizenship and Immigration Services, which was approximately $5.4 billion in FY2025. Where the surplus goes — and whether it will be reinvested in processing infrastructure or diverted to enforcement — is a question Congress has not yet answered.

Mullin's testimony did not address how the revenue is being allocated. But the fact that standard processing still takes seven and a half months, even as the agency collects unprecedented fees, suggests that capacity has not kept pace with demand.

## What Comes Next

The Roy bill faces a divided Congress and uncertain prospects. Even if it passes, its impact would not be felt until FY2027 or later. In the meantime, the $100,000 fee remains in effect, the backlog persists, and the fundamental tension at the heart of the H-1B program — between a labor market that demands skilled foreign workers and a political environment that views them with suspicion — shows no sign of resolution.

For the 200,000 who paid, the calculation was clear: the cost of waiting exceeded the cost of the fee. For the system they are navigating, the question is whether a program designed in the 1990s can sustain the weight of $20 billion in fees, 286,000 applications, and a political debate that treats each number as either a threat or a lifeline depending on who is reading it."""
}

print("Article 3: H-1B $100K fee")
insert_article(article3)
print()

print("Done. 3 articles published.")
