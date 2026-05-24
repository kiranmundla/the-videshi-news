#!/usr/bin/env python3
"""
Scrape US consulate wait times for Indian cities from travel.state.gov.
Stores results in Supabase consulate_wait_times table.
"""
import re, os, json, requests
from datetime import datetime

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SUPABASE_KEY:
    for p in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
        if os.path.exists(p):
            for line in open(p):
                if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                    SUPABASE_KEY = line.strip().split("=", 1)[1]
                    break
            if SUPABASE_KEY:
                break

HEADERS = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
}

WAIT_TIMES_URL = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"

# Indian consulates to track
INDIA_CONSULATES = {
    "Mumbai (Bombay)": ("mumbai", "Mumbai"),
    "New Delhi": ("new_delhi", "New Delhi"),
    "Chennai (Madras)": ("chennai", "Chennai"),
    "Hyderabad": ("hyderabad", "Hyderabad"),
    "Kolkata": ("kolkata", "Kolkata"),
}

# Also track popular third-country stamping locations
THIRD_COUNTRY = {
    "Dubai": ("dubai", "Dubai (UAE)"),
    "Singapore": ("singapore", "Singapore"),
    "Toronto": ("toronto", "Toronto (Canada)"),
    "Calgary": ("calgary", "Calgary (Canada)"),
    "London": ("london", "London (UK)"),
}

VISA_TYPES = [
    ("B1B2_avg", "Visitor (B1/B2) - Average Wait"),
    ("B1B2_next", "Visitor (B1/B2) - Next Available"),
    ("F_M_J", "Student/Exchange (F/M/J)"),
    ("H_L_O_P_Q", "Work Petition (H/L/O/P/Q)"),
    ("C_D", "Crew/Transit (C/D)"),
]


def parse_months(val: str):
    """Parse a wait time value like '7.5 Months', '< 0.5 Month', 'NA'."""
    import html as html_mod
    val = html_mod.unescape(val).strip()
    if val.upper() in ("NA", "N/A", "", "-"):
        return None
    # Handle "< 0.5 Month"
    val = val.replace("< ", "").replace("Months", "").replace("Month", "").strip()
    try:
        return float(val)
    except ValueError:
        return None


def scrape_wait_times():
    """Scrape the global wait times page and extract Indian consulate data."""
    print(f"Fetching: {WAIT_TIMES_URL}")
    resp = requests.get(WAIT_TIMES_URL, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        print(f"❌ HTTP {resp.status_code}")
        return []
    
    html = resp.text
    
    # Find the "Last updated" date
    updated_match = re.search(r'Last updated:\s*(\d{1,2}-[A-Z]+-\d{4})', html)
    source_updated = updated_match.group(1) if updated_match else "Unknown"
    print(f"  Source updated: {source_updated}")
    
    # Extract the main table
    table_match = re.search(r'<table[^>]*>(.*?)</table>', html, re.DOTALL | re.IGNORECASE)
    if not table_match:
        print("❌ No table found")
        return []
    
    table_html = table_match.group(1)
    
    # Parse rows
    row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    cell_pattern = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.DOTALL | re.IGNORECASE)
    
    # Target cities (merge India + third country)
    all_targets = {**INDIA_CONSULATES, **THIRD_COUNTRY}
    
    records = []
    now = datetime.utcnow().isoformat()
    
    for row_match in row_pattern.finditer(table_html):
        cells = []
        for cell_match in cell_pattern.finditer(row_match.group(1)):
            cell_text = re.sub(r'<[^>]+>', '', cell_match.group(1)).strip()
            import html as html_mod
            cell_text = html_mod.unescape(cell_text)
            cells.append(cell_text)
        
        if len(cells) < 6:
            continue
        
        city_name = cells[0].strip()
        
        # Check if this is one of our target cities
        matched_key = None
        for key in all_targets:
            if key.lower() in city_name.lower() or city_name.lower() in key.lower():
                matched_key = key
                break
        
        if not matched_key:
            continue
        
        consulate_code, consulate_display = all_targets[matched_key]
        
        # Columns: City | B1/B2 Avg | B1/B2 Next | F/M/J | H/L/O/P/Q | C/D
        b1b2_avg = parse_months(cells[1]) if len(cells) > 1 else None
        b1b2_next = parse_months(cells[2]) if len(cells) > 2 else None
        fmj = parse_months(cells[3]) if len(cells) > 3 else None
        hlopq = parse_months(cells[4]) if len(cells) > 4 else None
        cd = parse_months(cells[5]) if len(cells) > 5 else None
        
        print(f"  {consulate_display}: B1/B2 avg={b1b2_avg}, next={b1b2_next}, F/M/J={fmj}, H/L={hlopq}, C/D={cd}")
        
        # Create records for each visa type
        visa_data = [
            ("B1B2", "Visitor (B1/B2)", b1b2_avg, b1b2_next),
            ("F_M_J", "Student/Exchange (F/M/J)", None, fmj),
            ("H_L_O_P_Q", "Work Petition (H/L/O/P/Q)", None, hlopq),
            ("C_D", "Crew/Transit (C/D)", None, cd),
        ]
        
        for visa_type, visa_display, avg, nxt in visa_data:
            # For B1/B2 we have both avg and next; for others just next
            if avg is not None or nxt is not None:
                records.append({
                    "consulate": consulate_code,
                    "consulate_display": consulate_display,
                    "visa_type": visa_type,
                    "visa_type_display": visa_display,
                    "avg_wait_months": avg,
                    "next_available_months": nxt,
                    "source_updated": source_updated,
                })
    
    return records


def insert_records(records: list):
    """Insert records into Supabase."""
    if not records:
        return 0
    
    url = f"{SUPABASE_URL}/rest/v1/consulate_wait_times"
    resp = requests.post(url, headers=HEADERS, json=records)
    if resp.status_code in (200, 201):
        return len(records)
    else:
        print(f"❌ Insert error: {resp.status_code} {resp.text[:500]}")
        return 0


def main():
    records = scrape_wait_times()
    if records:
        inserted = insert_records(records)
        print(f"\n✅ Inserted {inserted} consulate wait time records")
    else:
        print("\n⚠️  No records scraped")


if __name__ == "__main__":
    main()
