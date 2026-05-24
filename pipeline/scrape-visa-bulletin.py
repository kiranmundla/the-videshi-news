#!/usr/bin/env python3
"""
Scrape US Visa Bulletin from travel.state.gov and store in Supabase.
Handles both Employment-Based and Family-Sponsored Final Action Dates and Dates for Filing.
"""
import re, sys, os, json, requests
from datetime import datetime, date

# ── Config ──
SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
if not SUPABASE_KEY:
    # Try loading from file
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
    "Prefer": "resolution=merge-duplicates",
}

def get_bulletin_url(year: int, month: int) -> str:
    """Get the correct URL for a visa bulletin. Oct-Dec bulletins are filed under the next calendar year's fiscal year."""
    month_name = MONTH_NAMES[month]
    # Fiscal year: Oct-Sep. Oct 2025 bulletin is under /2026/ (FY2026)
    if month >= 10:
        fy = year + 1
    else:
        fy = year
    return f"https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin/{fy}/visa-bulletin-for-{month_name}-{year}.html"

MONTH_NAMES = {
    1: "january", 2: "february", 3: "march", 4: "april",
    5: "may", 6: "june", 7: "july", 8: "august",
    9: "september", 10: "october", 11: "november", 12: "december"
}

# Date format in bulletins: "01SEP13", "15DEC22", "C", "U"
MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
}

def parse_visa_date(raw: str) -> tuple:
    """Parse a visa bulletin date string. Returns (date_str_or_None, status)."""
    raw = raw.strip().upper()
    if raw == "C":
        return (None, "current")
    if raw == "U":
        return (None, "unavailable")
    # Try to parse dates like "01SEP13", "15DEC22", "01APR23"
    m = re.match(r"(\d{2})([A-Z]{3})(\d{2})", raw)
    if m:
        day = int(m.group(1))
        mon = MONTH_MAP.get(m.group(2))
        yr2 = int(m.group(3))
        # Determine century: 00-50 -> 2000s, 51-99 -> 1900s
        year = 2000 + yr2 if yr2 <= 50 else 1900 + yr2
        if mon:
            return (f"{year}-{mon:02d}-{day:02d}", "dated")
    print(f"  ⚠️  Could not parse date: '{raw}'")
    return (None, "dated")


def fetch_bulletin_html(year: int, month: int) -> str:
    """Fetch the visa bulletin HTML page."""
    url = get_bulletin_url(year, month)
    print(f"Fetching: {url}")
    resp = requests.get(url, timeout=30, headers={"User-Agent": "Mozilla/5.0"})
    if resp.status_code != 200:
        print(f"  ❌ HTTP {resp.status_code}")
        return ""
    return resp.text


def extract_tables_from_html(html: str) -> list:
    """Extract all HTML tables as list of list of lists (rows x cells)."""
    tables = []
    # Simple regex-based table parser
    table_pattern = re.compile(r'<table[^>]*>(.*?)</table>', re.DOTALL | re.IGNORECASE)
    row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL | re.IGNORECASE)
    cell_pattern = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.DOTALL | re.IGNORECASE)
    
    for table_match in table_pattern.finditer(html):
        table_html = table_match.group(1)
        rows = []
        for row_match in row_pattern.finditer(table_html):
            cells = []
            for cell_match in cell_pattern.finditer(row_match.group(1)):
                # Strip HTML tags from cell content
                cell_text = re.sub(r'<[^>]+>', '', cell_match.group(1)).strip()
                cells.append(cell_text)
            if cells:
                rows.append(cells)
        if rows:
            tables.append(rows)
    return tables


def identify_visa_table(rows: list) -> dict:
    """Identify what type of visa table this is based on headers."""
    if not rows or len(rows) < 2:
        return None
    
    header = " ".join(rows[0]).upper()
    
    # Check if it's employment or family based
    is_employment = "EMPLOYMENT" in header or any("1ST" in " ".join(r).upper() or "2ND" in " ".join(r).upper() for r in rows[1:4])
    is_family = "FAMILY" in header or any("F1" == c.strip().upper() or "F2A" == c.strip().upper() for r in rows[1:4] for c in r)
    
    if not is_employment and not is_family:
        return None
    
    # Check column headers for countries
    # Expected: Category, All Chargeability, China, India, Mexico, Philippines
    info = {
        "type": "employment" if is_employment else "family",
        "header_row": rows[0],
        "data_rows": rows[1:] if len(rows) > 1 else [],
    }
    return info


# Employment-based category name normalization
EB_CATEGORIES = {
    "1ST": "EB-1",
    "2ND": "EB-2",
    "3RD": "EB-3",
    "OTHER WORKERS": "EB-3-Other",
    "4TH": "EB-4",
    "CERTAIN RELIGIOUS WORKERS": "EB-4-Religious",
    "5TH UNRESERVED": "EB-5-Unreserved",
    "5TH SET ASIDE: RURAL": "EB-5-Rural",
    "5TH SET ASIDE: HIGH UNEMPLOYMENT": "EB-5-HUA",
    "5TH SET ASIDE: INFRASTRUCTURE": "EB-5-Infrastructure",
}

FAMILY_CATEGORIES = {
    "F1": "F1",
    "F2A": "F2A", 
    "F2B": "F2B",
    "F3": "F3",
    "F4": "F4",
}


def normalize_category(raw: str, pref_type: str) -> str:
    """Normalize category name."""
    raw_upper = raw.upper().strip()
    
    if pref_type == "employment":
        for key, val in EB_CATEGORIES.items():
            if key in raw_upper:
                return val
        # Try partial match
        if raw_upper.startswith("1"):
            return "EB-1"
        if raw_upper.startswith("2"):
            return "EB-2"
        if raw_upper.startswith("3"):
            return "EB-3"
    else:
        for key, val in FAMILY_CATEGORIES.items():
            if raw_upper.startswith(key):
                return val
    
    return raw_upper


COUNTRY_COLUMNS = ["worldwide", "china", "india", "mexico", "philippines"]


def parse_visa_table(rows: list, pref_type: str, bulletin_month: int, bulletin_year: int, chart_type: str) -> list:
    """Parse a visa table into records."""
    records = []
    
    for row in rows:
        if len(row) < 6:
            continue
        
        cat_raw = row[0].strip()
        if not cat_raw or cat_raw.upper().startswith("EMPLOYMENT") or cat_raw.upper().startswith("FAMILY"):
            continue
        
        category = normalize_category(cat_raw, pref_type)
        if not category or category in ("", "---"):
            continue
        
        # Columns: category, worldwide, china, india, mexico, philippines
        for i, country in enumerate(COUNTRY_COLUMNS):
            if i + 1 >= len(row):
                break
            cell = row[i + 1].strip()
            if not cell or cell == "---":
                continue
            
            priority_date, status = parse_visa_date(cell)
            
            records.append({
                "bulletin_month": bulletin_month,
                "bulletin_year": bulletin_year,
                "preference_type": pref_type,
                "category": category,
                "chart_type": chart_type,
                "country": country,
                "priority_date": priority_date,
                "status": status,
            })
    
    return records


def scrape_bulletin(year: int, month: int) -> list:
    """Scrape a single visa bulletin and return records."""
    html = fetch_bulletin_html(year, month)
    if not html:
        return []
    
    tables = extract_tables_from_html(html)
    print(f"  Found {len(tables)} tables in HTML")
    
    all_records = []
    
    # We need to identify the 4 target tables:
    # 1. Employment Final Action Dates
    # 2. Employment Dates for Filing
    # 3. Family Final Action Dates
    # 4. Family Dates for Filing
    
    # Strategy: Look at the text BEFORE each table to determine its type
    # Better approach: parse tables in order — they appear in a known sequence
    
    # In the visa bulletin, the tables appear in this order:
    # Table 1: Family Final Action Dates
    # Table 2: Family Dates for Filing
    # Table 3: Employment Final Action Dates
    # Table 4: Employment Dates for Filing
    # Table 5+: Diversity Visa tables (ignore)
    
    employment_tables = []
    family_tables = []
    
    for table in tables:
        if len(table) < 2:
            continue
        # Check first data row for EB or F categories
        has_eb = False
        has_f = False
        for row in table:
            first_cell = row[0].upper().strip() if row else ""
            if any(x in first_cell for x in ["1ST", "2ND", "3RD", "4TH", "5TH", "OTHER WORKER", "CERTAIN RELIGIOUS"]):
                has_eb = True
            if re.match(r'^F[1234]', first_cell) or first_cell.startswith("F2"):
                has_f = True
        
        if has_eb and len(table[0]) >= 6:
            employment_tables.append(table)
        elif has_f and len(table[0]) >= 6:
            family_tables.append(table)
    
    print(f"  Employment tables: {len(employment_tables)}, Family tables: {len(family_tables)}")
    
    # Parse employment tables
    if len(employment_tables) >= 1:
        records = parse_visa_table(employment_tables[0], "employment", month, year, "final_action")
        all_records.extend(records)
        print(f"  Employment Final Action: {len(records)} records")
    if len(employment_tables) >= 2:
        records = parse_visa_table(employment_tables[1], "employment", month, year, "dates_for_filing")
        all_records.extend(records)
        print(f"  Employment Dates for Filing: {len(records)} records")
    
    # Parse family tables
    if len(family_tables) >= 1:
        records = parse_visa_table(family_tables[0], "family", month, year, "final_action")
        all_records.extend(records)
        print(f"  Family Final Action: {len(records)} records")
    if len(family_tables) >= 2:
        records = parse_visa_table(family_tables[1], "family", month, year, "dates_for_filing")
        all_records.extend(records)
        print(f"  Family Dates for Filing: {len(records)} records")
    
    return all_records


def upsert_records(records: list):
    """Upsert records into Supabase visa_bulletin table."""
    if not records:
        return 0
    
    url = f"{SUPABASE_URL}/rest/v1/visa_bulletin"
    
    # Batch insert (upsert) in chunks of 100
    total = 0
    for i in range(0, len(records), 100):
        batch = records[i:i+100]
        resp = requests.post(url, headers=HEADERS, json=batch)
        if resp.status_code in (200, 201):
            total += len(batch)
        else:
            print(f"  ❌ Insert error: {resp.status_code} {resp.text[:300]}")
    
    return total


def main():
    # Bulletins to scrape: Jan-June 2026
    bulletins = [
        (2026, 1), (2026, 2), (2026, 3), (2026, 4), (2026, 5), (2026, 6),
    ]
    
    # Allow command-line override
    if len(sys.argv) > 2:
        bulletins = [(int(sys.argv[1]), int(sys.argv[2]))]
    
    grand_total = 0
    for year, month in bulletins:
        print(f"\n{'='*60}")
        print(f"Scraping Visa Bulletin: {MONTH_NAMES[month].title()} {year}")
        print(f"{'='*60}")
        
        records = scrape_bulletin(year, month)
        if records:
            inserted = upsert_records(records)
            grand_total += inserted
            print(f"  ✅ Inserted {inserted} records for {MONTH_NAMES[month].title()} {year}")
        else:
            print(f"  ⚠️  No records scraped for {MONTH_NAMES[month].title()} {year}")
    
    print(f"\n{'='*60}")
    print(f"TOTAL: {grand_total} visa bulletin records inserted")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
