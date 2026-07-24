#!/usr/bin/env python3
"""Writer: July 1, 2026 news articles for The Videshi"""

import json
import os
import subprocess
from datetime import datetime, timezone

def load_env():
    """Load Supabase env vars."""
    env_file = os.path.expanduser("~/.env.supabase")
    env = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, val = line.split("=", 1)
                key = key.replace("export ", "").strip()
                val = val.strip().strip('"').strip("'")
                env[key] = val
                os.environ[key] = val
    return env

def insert_article(article, env):
    """Insert article into Supabase via curl."""
    url = env["SUPABASE_URL"]
    key = env["SUPABASE_SERVICE_ROLE_KEY"]
    
    payload = json.dumps(article)
    
    result = subprocess.run(
        [
            "curl", "-sS", "-X", "POST",
            f"{url}/rest/v1/p2_articles",
            "-H", f"apikey: {key}",
            "-H", f"Authorization: Bearer {key}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: return=representation",
            "-d", payload
        ],
        capture_output=True, text=True, timeout=30
    )
    
    resp = result.stdout
    try:
        data = json.loads(resp)
        if isinstance(data, list) and len(data) > 0:
            print(f"  ✓ Inserted: {data[0].get('headline', 'unknown')}")
            print(f"    ID: {data[0].get('id', 'N/A')}")
            return True
        elif isinstance(data, dict) and data.get("message"):
            print(f"  ✗ Error: {data.get('message')}")
            return False
        else:
            print(f"  ? Response: {resp[:200]}")
            return False
    except json.JSONDecodeError:
        print(f"  ✗ Parse error: {resp[:200]}")
        return False


def main():
    env = load_env()
    now = datetime.now(timezone.utc).isoformat()
    
    articles = []

    # =========================================================================
    # ARTICLE 1: SCOTUS Overturns Humphrey's Executor
    # =========================================================================
    articles.append({
        "headline": "The Supreme Court Just Killed a 90-Year Rule That Kept Agency Chiefs Safe From the President",
        "subheadline": "The 6-3 ruling overturns Humphrey's Executor, giving Trump — and every future president — the power to fire the heads of more than two dozen independent agencies at will. For Indian Americans in government and the industries these agencies oversee, the stakes are enormous.",
        "slug": "scotus-overturns-humphreys-executor-presidential-power-independent-agencies-20260701",
        "category": "news",
        "vertical": "governance",
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/da/Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg/1280px-Panorama_of_United_States_Supreme_Court_Building_at_Dusk.jpg",
        "image_caption": "The United States Supreme Court building in Washington, D.C., at dusk",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Indian Americans hold leadership positions across federal agencies and dominate the tech and finance sectors these regulators oversee — a shift in agency independence directly affects their careers, investments, and consumer protections.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "CNN", "url": "https://www.cnn.com/"},
            {"name": "USA Today", "url": "https://www.usatoday.com/"},
            {"name": "Washington Examiner", "url": "https://www.washingtonexaminer.com/"}
        ]),
        "body": """On Monday, the Supreme Court overturned *Humphrey's Executor v. United States*, a 90-year-old precedent that had shielded the heads of independent federal agencies from being fired by the president at will. The 6-3 ruling, split along ideological lines, is arguably the most consequential decision of the court's 2025-26 term — and legal scholars say it may be the single largest expansion of presidential power in the court's history.

"If anything more is left of Humphrey's, we overrule it," Chief Justice John Roberts wrote for the majority. "Humphrey's has for decades been a result in search of a rationale."

The case, *Trump v. Slaughter*, began when President Trump fired Federal Trade Commission Chair Lina Khan and Commissioner Rebecca Slaughter, arguing that the statutory protections shielding FTC members from removal without cause were unconstitutional. The court agreed.

## What Changed

Since 1935, Humphrey's Executor had insulated more than two dozen independent agencies from presidential interference. The Federal Trade Commission, the Federal Communications Commission, the Securities and Exchange Commission, the Consumer Product Safety Commission, the Nuclear Regulatory Commission — all operated under the premise that their leaders could only be removed for "inefficiency, neglect of duty, or malfeasance in office."

That's over now.

The ruling means the president can fire the leaders of these agencies for any reason — policy disagreements, political loyalty, or simply wanting someone else in the chair. Congress can still set qualifications for the roles, but it can no longer insulate appointees from dismissal.

The court carved out one significant exception: the Federal Reserve. In a companion ruling, *Trump v. Cook*, the same 6-3 majority held that the president cannot fire Federal Reserve governors at will, citing the unique nature of the central bank and its role in monetary policy. Justice Clarence Thomas dissented on this point, arguing that "before the Federal Reserve Act, the American tradition of central banking consisted mainly of the First and Second Banks of the United States."

## "A Power Unknown Even to the English Crown"

Justice Sonia Sotomayor, joined by Justices Elena Kagan and Ketanji Brown Jackson, read an impassioned dissent from the bench — a rare signal of the depth of her disagreement.

"The court gives the president a power unknown even to the English Crown against which the Founders revolted," Sotomayor wrote. She warned the decision "undoes centuries of political practice" and would lead to "only chaos" as agency leadership becomes subject to the whims of electoral cycles.

Gautam Hans, a professor at Cornell Law School, called the ruling "the triumph of decades of conservative advocacy." He noted that despite the administration's losses on tariffs and birthright citizenship earlier in the term, "they are probably quite happy with that prize."

## The Rohit Chopra Precedent

For the Indian American community, the implications are already visible. In February 2025, President Trump fired Rohit Chopra, the Indian American director of the Consumer Financial Protection Bureau, who had earned a reputation as one of the most aggressive consumer advocates in the agency's history. Under Chopra's leadership, the CFPB had secured nearly $20 billion in consumer relief, taken on major banks over Zelle fraud, and pushed to cap credit card late fees.

At the time, the firing was legally straightforward — the Supreme Court had already ruled in 2020 that the president could dismiss a single CFPB director at will. But the Humphrey's Executor ruling now extends that power across the entire constellation of independent agencies. Every agency chief who previously enjoyed the protection of a fixed term now serves at the president's pleasure.

Consumer advocacy groups warned the ruling could chill independent regulation. "Chopra's firing was a preview," said Delicia Hand, senior director of the digital marketplace at Consumer Reports. "Now the same playbook can be used at the FTC, the SEC, the FCC — any agency where enforcement conflicts with political priorities."

## What It Means for Tech, Finance, and the Diaspora

The agencies affected by the ruling regulate virtually every sector where Indian Americans have outsized influence. The FTC oversees antitrust enforcement in the tech industry, where Indian-origin executives lead companies from Google to Microsoft to Adobe. The SEC regulates the financial markets where Indian Americans are among the most active retail and institutional investors. The FCC governs telecommunications policy, including spectrum allocation and broadband access.

The ruling also has implications for the regulatory environment around immigration-adjacent technology. Companies that employ large numbers of H-1B workers operate under compliance frameworks shaped by agencies that are now more directly subject to presidential control.

"This isn't just about who sits in the chair," said Jenny Breen, a professor at Syracuse University College of Law. "It's about whether agencies can make long-term policy that survives from one administration to the next. Independent agencies were designed to provide continuity. That design has now been dismantled."

## The Bigger Picture

The Humphrey's Executor ruling capped a Supreme Court term that repeatedly tested the boundaries of presidential authority. The conservative majority dealt Trump three significant losses — striking down his sweeping tariffs, upholding birthright citizenship, and blocking his attempt to fire Federal Reserve Governor Lisa Cook. But on the whole, the court embraced what George Mason University law professor Robert Luther III called "a robust vision of executive power."

The contrast with the Biden era is striking. "This court had essentially the same composition of justices during President Biden's term but was more likely to rule against his major exertions of presidential power," Breen observed. "The comparison is striking."

For the estimated 5.4 million Indian Americans living in the United States — many of them working in the technology, finance, and government sectors most directly affected by independent agency oversight — the ruling marks a fundamental shift in how the federal government operates. The agencies that regulate their industries, protect their investments, and enforce the consumer laws they rely on are now more firmly under the control of whoever occupies the Oval Office.

Whether that produces better governance or worse depends on who you ask. But after 90 years of relative stability, the answer is no longer academic."""
    })

    # =========================================================================
    # ARTICLE 2: India's First Jet Fuel Price Cut + IndiGo Lite Fares
    # =========================================================================
    articles.append({
        "headline": "India Just Cut Jet Fuel Prices for the First Time Since the Iran War. IndiGo Is Already Passing It On.",
        "subheadline": "Aviation turbine fuel drops ₹5 per litre to ₹110 in Delhi — the first reduction since the Middle East conflict sent prices to record highs. On the same day, India's largest airline launches a stripped-down fare class that could reshape how the diaspora books flights home.",
        "slug": "india-atf-jet-fuel-price-cut-indigo-lite-fares-aviation-iran-war-20260701",
        "category": "news",
        "vertical": "economy",
        "status": "review",
        "is_editorial": False,
        "published_at": now,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg/3840px-IndiGo_Airbus_A320neo_F-WWDG_%28to_VT-ITI%29_%2828915135713%29.jpg",
        "image_caption": "An IndiGo Airbus A320neo aircraft in the airline's signature livery",
        "image_attribution": "Wikimedia Commons",
        "diaspora_angle": "Jet fuel accounts for up to 40% of airline operating costs — this price cut and IndiGo's new budget fare could make trips to India measurably cheaper for millions of NRIs who fly home at least once a year.",
        "sources": json.dumps([
            {"name": "Reuters", "url": "https://www.reuters.com/"},
            {"name": "Press Trust of India", "url": "https://www.ptinews.com/"},
            {"name": "Livemint", "url": "https://www.livemint.com/"},
            {"name": "CNN", "url": "https://www.cnn.com/"}
        ]),
        "body": """Two things happened on July 1 that, taken together, signal a turning point for India's aviation sector — and for the millions of NRIs who dread opening their inbox to find a fare alert.

India's state-owned oil marketing companies cut the price of aviation turbine fuel by nearly ₹5 per litre, bringing the rate in Delhi to approximately ₹110. It is the first downward revision in jet fuel prices since the U.S.-Iran war sent global oil costs spiralling to record highs earlier this year.

And on the same day, IndiGo — India's largest airline by market share — launched a new stripped-down fare class called "IndiGo Lite," offering lower prices for passengers willing to travel with only cabin baggage.

Neither development alone is transformative. Together, they mark the beginning of a structural shift in India's aviation economics — one that has been months in the making.

## The First Cut Is the Deepest

Jet fuel accounts for up to 40 per cent of an Indian airline's operating costs. When the Iran war erupted in February and the Strait of Hormuz was effectively shut down, ATF prices roughly doubled. Airlines responded the only way they could: they raised fares, cut routes, and added fees that hadn't existed before. Air India introduced a basic economy fare stripped of complimentary meals. Smaller carriers eliminated unprofitable sectors entirely.

The human cost was felt most acutely by the diaspora. Round-trip fares between the U.S. and India jumped 15 to 20 per cent, according to Deutsche Bank Securities data tracking hundreds of published fares. For a family of four flying from San Francisco to Delhi and back for a summer wedding, the increase could mean an additional $800 to $1,200.

Now, with Brent crude trading at roughly $71 a barrel — down 43 per cent from the war's peak of $126 in April — the economics have shifted. The ATF price cut reflects this decline, though it remains modest relative to the scale of the earlier increase.

"This is a first step, not the last," said a Mumbai-based industry analyst who declined to be named. "ATF was at ₹115 under the government's stabilisation scheme. It's now ₹110. Before the war, it was closer to ₹85. There's a long way to go before we're back to normal."

## IndiGo's Calculus

IndiGo's new Lite fare is available for booking starting July 1, with travel effective July 15. The fare applies across domestic and international flights and provides passengers with a cabin bag allowance of up to 7 kilograms and an auto-assigned seat at no additional cost. Checked baggage, preferred seats, and add-ons carry extra charges.

The move mirrors a global trend of fare unbundling that has reshaped aviation economics in Europe and the United States. Ryanair, Spirit Airlines (before its closure in May), and others proved that passengers will accept fewer amenities in exchange for a lower base price. Indian airlines had largely resisted the model — until the Iran war forced them to find new ways to fill seats on increasingly expensive routes.

IndiGo's timing is strategic. The carrier controls roughly 60 per cent of India's domestic market, and its international network has expanded aggressively over the past two years. By introducing a budget tier, IndiGo can lower its entry-level fares to compete with Air India's recently launched basic economy option while capturing revenue from passengers who choose to add services.

"The fare unbundling game is about to begin in earnest in India," said Pankaj Pandey, head of retail research at ICICI Securities. "IndiGo is not going to be the last carrier to strip down fares."

## The Government's Stabilisation Bet

The ATF price cut also interacts with the government's ₹10,000 crore Aviation Turbine Fuel Price Stabilisation Fund, which was approved in early June. Under the scheme, airlines that opt in pay a fixed price of ₹115 per litre — regardless of market fluctuations — for up to three years. When global prices fall below that level, the difference is used to replenish the fund.

So far, no major Indian airline has opted into the scheme. The reluctance is understandable: with global oil prices already declining and the stabilised rate set at ₹115, airlines that stayed out are now paying ₹110 — less than the scheme's fixed rate. The opt-in only makes sense as insurance against a price spike, and with the U.S.-Iran talks in Doha producing what Qatar's foreign ministry called "positive progress," the market is pricing in continued de-escalation.

The government also lifted restrictions on diesel purchases that had been imposed on June 11 amid war-related supply disruptions. Commercial buyers can once again purchase diesel without daily caps, a relief for transporters and logistics companies that had been operating with constrained fuel access.

## What Changes for Travellers

For the diaspora, the practical implications are still developing. Domestic fares within India should see downward pressure as IndiGo's Lite fare forces competitors to respond. International fares on routes to the United States, United Kingdom, and Canada — where NRI traffic is heaviest — are more complex. Jet fuel is priced differently at international airports, and airlines' revenue management systems calibrate fares based on demand and competition rather than cost alone.

Delta CEO Ed Bastian said last week that fares were at the "right level" despite what he described as "meaningfully" lower fuel costs. The comment drew criticism from consumer advocates who noted that fuel savings were not being passed through to passengers.

But the trend lines are clear. Oil prices at their lowest in four months. ATF costs declining for the first time since the war. India's largest airline introducing a budget fare class. If the Hormuz situation continues to stabilise — a significant "if" — airfares have room to fall.

For NRIs planning trips home this year, the calculus is shifting. Not dramatically, not overnight. But for the first time since February, it's shifting in the right direction."""
    })

    # =========================================================================
    # Insert articles
    # =========================================================================
    print(f"\nInserting {len(articles)} articles...")
    for i, article in enumerate(articles, 1):
        print(f"\n[{i}/{len(articles)}] {article['headline'][:80]}...")
        insert_article(article, env)

    print("\nDone.")


if __name__ == "__main__":
    main()
