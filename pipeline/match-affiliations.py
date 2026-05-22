#!/usr/bin/env python3
"""
Match doctors to hospital/health system affiliations.
Uses stricter matching - only matches on ADDRESS (not name) to avoid
false positives like "Rushita" matching "Rush University".
Name matching only for very specific patterns like "| Kaiser Permanente".
"""

import os, re, requests

env = {}
for line in open(os.path.expanduser("~/.env.supabase")):
    line = line.strip()
    if '=' in line and not line.startswith('#'):
        k, v = line.split('=', 1)
        env[k] = v

SUPABASE_URL = env['SUPABASE_URL']
SERVICE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']

headers = {
    'apikey': SERVICE_KEY,
    'Authorization': f'Bearer {SERVICE_KEY}',
    'Content-Type': 'application/json',
    'Prefer': 'return=minimal'
}

# Address-only patterns (match in address field only — no name matching to avoid false positives)
ADDRESS_SYSTEMS = [
    # Bay Area
    ("Kaiser Permanente", [r"\bkaiser\b"]),
    ("Sutter Health / PAMF", [r"\bsutter\b", r"\bpamf\b", r"\bpalo alto medical foundation\b"]),
    ("John Muir Health", [r"\bjohn muir\b"]),
    ("Stanford Health Care", [r"\bstanford\b(?!.*university)"]),
    ("UCSF Health", [r"\bucsf\b"]),
    ("El Camino Health", [r"\bel camino\b"]),
    ("Washington Hospital", [r"\bwashington hospital\b", r"\bwashington township\b"]),
    # NYC/NJ
    ("Mount Sinai", [r"\bmount sinai\b", r"\bmt\.?\s*sinai\b"]),
    ("NYU Langone", [r"\bnyu langone\b"]),
    ("NewYork-Presbyterian", [r"\bpresbyterian\b.*\bhospital\b", r"\bnyp\b"]),
    ("Northwell Health", [r"\bnorthwell\b"]),
    ("Hackensack Meridian", [r"\bhackensack\b.*\bmedical\b"]),
    # Chicago
    ("Northwestern Medicine", [r"\bnorthwestern\b.*\b(memorial|medical|medicine)\b"]),
    ("Rush University Medical", [r"\brush\b.*\b(university|medical|hospital)\b"]),
    ("Advocate Health", [r"\badvocate\b.*\b(health|medical|hospital)\b"]),
    # TX
    ("Houston Methodist", [r"\bhouston methodist\b"]),
    ("Memorial Hermann", [r"\bmemorial hermann\b"]),
    ("Baylor Scott & White", [r"\bbaylor\b.*\b(medical|hospital|scott)\b"]),
    ("UT Southwestern", [r"\but southwestern\b", r"\butsw\b"]),
    # LA
    ("Cedars-Sinai", [r"\bcedars[\s-]?sinai\b"]),
    ("UCLA Health", [r"\bucla\b.*\b(health|medical)\b"]),
    ("Providence", [r"\bprovidence\b.*\b(medical|hospital|health)\b"]),
    # Seattle
    ("Virginia Mason", [r"\bvirginia mason\b"]),
    ("Swedish Medical", [r"\bswedish\b.*\bmedical\b"]),
    ("UW Medicine", [r"\buw\b.*\bmedicine\b", r"\buniversity of washington\b.*\bmedical\b"]),
    # Atlanta
    ("Emory Healthcare", [r"\bemory\b.*\b(health|medical|hospital|clinic)\b"]),
    ("Piedmont Healthcare", [r"\bpiedmont\b.*\b(health|medical|hospital)\b"]),
    # DC/MD/VA
    ("MedStar Health", [r"\bmedstar\b"]),
    ("Johns Hopkins", [r"\bjohns hopkins\b"]),
    ("Inova Health", [r"\binova\b"]),
    # Boston
    ("Mass General Brigham", [r"\bmass general\b", r"\bbrigham\b.*\b(women|hospital)\b"]),
    ("Beth Israel", [r"\bbeth israel\b"]),
]

# Name patterns - only very explicit markers like "| Kaiser Permanente" or "at Sutter Health"
NAME_EXPLICIT = [
    ("Kaiser Permanente", [r"\|\s*kaiser\s+permanente", r"\bat\s+kaiser\b", r"kaiser\s+permanente"]),
    ("Sutter Health", [r"\|\s*sutter", r"\bat\s+sutter\b"]),
    ("Stanford Health Care", [r"\|\s*stanford", r"\bat\s+stanford\b"]),
    ("UCSF Health", [r"\|\s*ucsf", r"\bat\s+ucsf\b"]),
    ("John Muir Health", [r"\|\s*john muir", r"\bat\s+john muir\b"]),
    ("Mount Sinai", [r"\|\s*mount sinai", r"\bat\s+mount sinai\b"]),
    ("NYU Langone", [r"\|\s*nyu langone", r"\bat\s+nyu\b"]),
    ("Northwestern Medicine", [r"\|\s*northwestern", r"\bat\s+northwestern\b"]),
    ("Houston Methodist", [r"\|\s*houston methodist"]),
    ("Cedars-Sinai", [r"\|\s*cedars", r"\bat\s+cedars\b"]),
]

def match_affiliation(name, address):
    name_lower = (name or "").lower()
    addr_lower = (address or "").lower()
    
    # Check explicit name patterns first (highest confidence)
    for system, patterns in NAME_EXPLICIT:
        for pat in patterns:
            if re.search(pat, name_lower):
                return system
    
    # Check address patterns
    for system, patterns in ADDRESS_SYSTEMS:
        for pat in patterns:
            if re.search(pat, addr_lower):
                return system
    
    return None

def main():
    print("Fetching all Doctors & Healthcare listings...")
    
    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/directory_listings"
        f"?select=id,name,address"
        f"&category=eq.Doctors %26 Healthcare"
        f"&limit=1000",
        headers=headers
    )
    
    listings = r.json()
    print(f"Found {len(listings)} listings\n")
    
    matched = 0
    affiliations = {}
    
    for listing in listings:
        aff = match_affiliation(listing.get('name', ''), listing.get('address', ''))
        
        if aff:
            r = requests.patch(
                f"{SUPABASE_URL}/rest/v1/directory_listings?id=eq.{listing['id']}",
                headers=headers,
                json={"affiliation": aff}
            )
            if r.status_code < 300:
                matched += 1
                affiliations[aff] = affiliations.get(aff, 0) + 1
                print(f"  ✓ {listing['name'][:50]:50s} → {aff}")
    
    print(f"\n{'='*60}")
    print(f"Matched {matched}/{len(listings)} doctors\n")
    for aff, count in sorted(affiliations.items(), key=lambda x: -x[1]):
        print(f"  {count:4d}  {aff}")

if __name__ == "__main__":
    main()
