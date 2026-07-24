#!/usr/bin/env python3
import json, os, requests
from pathlib import Path

env_file = Path.home() / ".env.supabase"
for line in env_file.read_text().strip().splitlines():
    if "=" in line and not line.startswith("#"):
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

SB_URL = os.environ["SUPABASE_URL"]
SB_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {
    "apikey": SB_KEY,
    "Authorization": f"Bearer {SB_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=representation",
}

# Extra paragraphs to append (inserted before final paragraph where possible)
ADDS = {
"etihad-business-class-flash-sale-india-origin-us-nri-autumn-20260625":
"""

## How it stacks up against the alternatives

It helps to anchor the deal against what the diaspora actually pays. A nonstop business-class round trip on Air India between a US gateway and Delhi or Mumbai is frequently quoted at $5,500–7,700 in peak months — the kind of price that pushes most families to economy and a long, upright night. Even Emirates and Qatar, the usual one-stop discounters, rarely dip below the mid-$3,000s in business outside a sale. Etihad's promotional floor, converted, lands well under that for eligible India-origin routings, which is why this week is worth the spreadsheet.

There is also a loyalty angle the savvy traveller will exploit. Business-class fares on these promos still earn full or near-full miles and tier credit, so a single discounted round trip can reset an Etihad Guest balance or push a frequent flyer toward status that pays off on future India runs. For a community that flies this corridor more than almost any other, status is not vanity — it is shorter queues, free seat selection, and lounge access for the parents who travel alone.""",

"india-multi-crew-pilot-licence-simulator-training-shortage-nri-20260625":
"""

## The scale of the shortage

To understand why the regulator is even considering this, look at the order books. Between them, IndiGo and Air India have committed to well over 1,000 new aircraft over the coming decade — one of the largest fleet expansions in aviation history. Each wide-body needs multiple crews, and a single Boeing 787 or Airbus A350 on a US route burns through pilots faster than a domestic turboprop. India is already poaching captains from abroad and paying signing premiums, and training schools cannot turn out qualified first officers fast enough to keep pace. The MCPL is, in plain terms, an attempt to widen the funnel without lowering the floor.

That is exactly where diaspora skepticism is healthy rather than alarmist. The aviation world has seen what happens when commercial pressure outruns training rigor, and India's own recent safety record has kept public trust on edge. The reassuring part is that the MCPL is not a shortcut invented in Delhi — it is an ICAO standard flown safely across dozens of countries. The worrying part is that a standard is only as good as the oversight enforcing it. The diaspora's stake is simple: the same airlines being asked to crew more US nonstops are the ones helping design how their pilots get made.""",

"vande-bharat-sleeper-overnight-train-nri-metro-hometown-connector-20260625":
"""

## A different kind of India trip

There is a softer argument for the sleeper that the diaspora feels more than it calculates. For second-generation NRIs and the kids being brought "back home," the overnight train is not just transport — it is the part of India that doesn't exist abroad. The morning chai through the window, the slow reveal of a landscape changing from city to paddy field to hills, the shared compartment conversations: a clean, modern sleeper makes that experience accessible to families who'd otherwise fly over it in 90 minutes and miss it entirely. The Vande Bharat Sleeper keeps the romance while removing the discomfort that made older relatives say "just book the flight."

It is also a quiet bet on the parts of India the diaspora keeps meaning to see. The Northeast, the Himalayan foothills, the heritage corridors of the Gangetic plain — these are the "next time" destinations that never fit the itinerary because the connection was too painful. As the sleeper network grows, those trips move from aspiration to plan. The airports will keep getting the splashy inaugurations, but the train is where the diaspora's India actually opens up.""",
}

for slug, extra in ADDS.items():
    # fetch current body
    r = requests.get(f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id,body", headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        print(f"❌ not found: {slug}")
        continue
    aid = rows[0]["id"]
    body = rows[0]["body"]
    # insert extra before the final paragraph (after last \n\n)
    idx = body.rstrip().rfind("\n\n")
    if idx == -1:
        new_body = body.rstrip() + extra
    else:
        new_body = body[:idx] + extra + "\n" + body[idx:]
    wc = len(new_body.split())
    rp = requests.patch(f"{SB_URL}/rest/v1/p2_articles?id=eq.{aid}", headers=HEADERS,
                        json={"body": new_body}, timeout=30)
    rp.raise_for_status()
    print(f"✅ {slug} -> {wc} words")
