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

# Additional paragraphs to insert before the final "## What's next" / "## The bottom line" / "## The caveats" sections.

add1 = """
## The legacy advantage

The reversal carries an irony the diaspora will appreciate. The companies winning — TVS, Bajaj, Hero — are the same century-old names that NRIs grew up watching their fathers ride to work in India. They were written off as dinosaurs when Ola arrived promising a Silicon Valley reinvention of the scooter. Instead, their decades of dealer relationships, service networks and supply-chain discipline turned out to be exactly the assets an electric transition rewards. Bajaj's Chetak and TVS's iQube now sit among the country's best-selling EVs, and Honda, entering from a base of just 201 units a year ago, has begun to scale. The lesson echoes well beyond scooters: in hardware, the boring competencies compound.
"""

add2 = """
## A different kind of homecoming

There is a generational shift embedded in this too. The founders of these deep-tech startups are increasingly returnees themselves — former ISRO engineers, ex-Google researchers, IIT graduates who did a tour in Silicon Valley and came back. Skyroot was founded by two former ISRO propulsion engineers; Agnikul grew out of IIT Madras. For the diaspora, that changes the texture of the opportunity. Backing Indian deep tech is no longer a charitable bet on a developing market; it is a bet on peers, on people who trained in the same labs and now believe the frontier work can be done from Hyderabad or Chennai as well as from Mountain View.
"""

add3 = """
## The orchestration layer

The optimists have a point worth taking seriously. The same shift that threatens entry-level coding creates a premium on a different skill: designing, governing and orchestrating fleets of agents, work that demands systems thinking rather than syntax. IBM, Microsoft and the Indian IT majors are all racing to reposition around exactly this — Wipro built a center to run Anthropic's Claude, Cognizant wired ServiceNow's agents into its own, and Infosys is retraining staff for "agent operations." For Indian engineers willing to climb that curve, the agentic era could be a promotion rather than a pink slip. The catch is that the climb is steep, and the rung that used to let new graduates onto the ladder is the one being sawn off.
"""

updates = [
    ("ola-electric-india-ev-two-wheeler-shakeout-tvs-ather-nri-investors-20260619", "## What's next", add1),
    ("bharat-innovates-2026-deep-tech-funding-nice-nri-investors-space-semic-20260619", "## The caveats", add2),
    ("nvidia-jensen-huang-computex-agentic-ai-vera-cpu-indian-engineers-it-j-20260619", "## The bottom line", add3),
]

for slug, anchor, addition in updates:
    r = requests.get(f"{SB_URL}/rest/v1/p2_articles?slug=eq.{slug}&select=id,body", headers=HEADERS, timeout=30)
    r.raise_for_status()
    rows = r.json()
    if not rows:
        print(f"❌ not found: {slug}")
        continue
    art_id = rows[0]["id"]
    body = rows[0]["body"]
    if anchor not in body:
        print(f"⚠ anchor '{anchor}' not in {slug}; appending at end")
        new_body = body.rstrip() + "\n" + addition
    else:
        new_body = body.replace(anchor, addition.strip() + "\n\n" + anchor, 1)
    pr = requests.patch(f"{SB_URL}/rest/v1/p2_articles?id=eq.{art_id}", headers=HEADERS,
                        json={"body": new_body}, timeout=30)
    pr.raise_for_status()
    print(f"✅ {slug} → {len(new_body.split())} words")
