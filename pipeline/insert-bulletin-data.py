#!/usr/bin/env python3
"""Insert July and August 2026 visa bulletin data into Supabase."""
import os, json, subprocess

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://lboecaekpynbpyijrbfz.supabase.co")
SUPABASE_KEY = ""
for p in [os.path.expanduser("~/.env.supabase"), os.path.expanduser("~/workspace/.env.supabase")]:
    if os.path.exists(p):
        for line in open(p):
            if line.startswith("SUPABASE_SERVICE_ROLE_KEY="):
                SUPABASE_KEY = line.strip().split("=", 1)[1]
                break
        if SUPABASE_KEY:
            break

def parse_date(raw):
    """Parse date like '01JAN14' or 'C' or 'U'."""
    raw = raw.strip().upper()
    if raw == "C":
        return None, "current"
    if raw in ("U", "UNAVAILABLE"):
        return None, "unavailable"
    
    MONTH_MAP = {
        "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
        "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12
    }
    
    import re
    # Format: 01JAN14 or 15DEC22
    m = re.match(r"(\d{1,2})([A-Z]{3})(\d{2})", raw)
    if m:
        day = int(m.group(1))
        mon = MONTH_MAP.get(m.group(2))
        yr2 = int(m.group(3))
        year = 2000 + yr2 if yr2 <= 50 else 1900 + yr2
        if mon:
            return f"{year}-{mon:02d}-{day:02d}", "dated"
    
    # Format: M-DD-YY or MM-DD-YY (from shusterman)
    m = re.match(r"(\d{1,2})-(\d{1,2})-(\d{2,4})", raw)
    if m:
        mon = int(m.group(1))
        day = int(m.group(2))
        yr = int(m.group(3))
        if yr < 100:
            yr = 2000 + yr if yr <= 50 else 1900 + yr
        return f"{yr}-{mon:02d}-{day:02d}", "dated"
    
    print(f"  ⚠️  Could not parse: '{raw}'")
    return None, "dated"


def build_records(month, year, pref_type, chart_type, data):
    """Build records from structured data.
    data: list of (category, worldwide, china, india, mexico, philippines)
    """
    countries = ["worldwide", "china", "india", "mexico", "philippines"]
    records = []
    for row in data:
        cat = row[0]
        for i, country in enumerate(countries):
            date_str, status = parse_date(row[i + 1])
            records.append({
                "bulletin_month": month,
                "bulletin_year": year,
                "category": cat,
                "country": country,
                "chart_type": chart_type,
                "priority_date": date_str,
                "status": status,
                "preference_type": pref_type,
            })
    return records


# ============================================================
# JULY 2026 DATA (from travel.state.gov direct)
# ============================================================

# Employment-Based Final Action Dates - July 2026
july_eb_fa = [
    ("EB-1", "C", "01JUN23", "15OCT22", "C", "C"),
    ("EB-2", "C", "01SEP21", "U", "C", "C"),
    ("EB-3", "01AUG24", "22DEC21", "01JAN14", "01AUG24", "01AUG23"),
    ("EB-3-Other", "01MAR22", "01APR19", "01JAN14", "01MAR22", "01DEC21"),
    ("EB-4", "15SEP22", "15SEP22", "15SEP22", "15SEP22", "15SEP22"),
    ("EB-4-Religious", "15SEP22", "15SEP22", "15SEP22", "15SEP22", "15SEP22"),
    ("EB-5-Unreserved", "C", "01DEC16", "U", "C", "C"),
    ("EB-5-Set-Aside-Rural", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-High-Unemployment", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-Infrastructure", "C", "C", "C", "C", "C"),
]

# Employment-Based Filing Dates - July 2026
july_eb_ff = [
    ("EB-1", "C", "01DEC23", "01DEC23", "C", "C"),
    ("EB-2", "C", "01JAN22", "15JAN15", "C", "C"),
    ("EB-3", "C", "01JAN22", "15JAN15", "C", "01JAN24"),
    ("EB-3-Other", "01AUG22", "01OCT19", "15JAN15", "01AUG22", "01AUG22"),
    ("EB-4", "01JAN23", "01JAN23", "01JAN23", "01JAN23", "01JAN23"),
    ("EB-4-Religious", "01JAN23", "01JAN23", "01JAN23", "01JAN23", "01JAN23"),
    ("EB-5-Unreserved", "C", "01MAR17", "01MAY24", "C", "C"),
    ("EB-5-Set-Aside-Rural", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-High-Unemployment", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-Infrastructure", "C", "C", "C", "C", "C"),
]

# Family-Based Final Action Dates - July 2026
july_fb_fa = [
    ("F1", "01FEB18", "01FEB18", "01FEB18", "08NOV07", "01MAY13"),
    ("F2A", "01JAN25", "01JAN25", "01JAN25", "01JAN24", "01JAN25"),
    ("F2B", "22NOV17", "22NOV17", "22NOV17", "15FEB09", "15MAY13"),
    ("F3", "15APR12", "15APR12", "15APR12", "01JUN01", "22FEB06"),
    ("F4", "01JAN09", "01JAN09", "01NOV06", "08APR01", "01AUG07"),
]

# Family-Based Filing Dates - July 2026
july_fb_ff = [
    ("F1", "01JAN19", "01JAN19", "01JAN19", "01OCT08", "22APR15"),
    ("F2A", "C", "C", "C", "C", "C"),
    ("F2B", "08JUN18", "08JUN18", "08JUN18", "15MAY10", "01OCT13"),
    ("F3", "08DEC12", "08DEC12", "08DEC12", "15JUL01", "08AUG06"),
    ("F4", "01MAR10", "01MAR10", "15DEC06", "30APR01", "22MAR08"),
]


# ============================================================
# AUGUST 2026 DATA (from shusterman.com)
# ============================================================

# Employment-Based Final Action Dates - August 2026
aug_eb_fa = [
    ("EB-1", "C", "7-01-23", "10-15-22", "C", "C"),
    ("EB-2", "C", "9-01-21", "U", "C", "C"),
    ("EB-3", "9-01-24", "1-01-22", "1-01-14", "9-01-24", "8-01-23"),
    ("EB-3-Other", "4-01-22", "5-01-19", "1-01-14", "4-01-22", "12-01-21"),
    ("EB-4", "10-15-22", "10-15-22", "10-15-22", "10-15-22", "10-15-22"),
    ("EB-4-Religious", "10-15-22", "10-15-22", "10-15-22", "10-15-22", "10-15-22"),
    ("EB-5-Unreserved", "C", "12-01-16", "U", "C", "C"),
    ("EB-5-Set-Aside-Rural", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-High-Unemployment", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-Infrastructure", "C", "C", "C", "C", "C"),
]

# Employment-Based Filing Dates - August 2026
aug_eb_ff = [
    ("EB-1", "C", "12-01-23", "12-01-23", "C", "C"),
    ("EB-2", "C", "1-01-22", "1-15-15", "C", "C"),
    ("EB-3", "C", "1-08-22", "1-15-15", "C", "1-01-24"),
    ("EB-3-Other", "8-01-22", "10-01-19", "1-15-15", "8-01-22", "8-01-22"),
    ("EB-4", "1-01-23", "1-01-23", "1-01-23", "1-01-23", "1-01-23"),
    ("EB-4-Religious", "1-01-23", "1-01-23", "1-01-23", "1-01-23", "1-01-23"),
    ("EB-5-Unreserved", "C", "3-01-17", "5-01-24", "C", "C"),
    ("EB-5-Set-Aside-Rural", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-High-Unemployment", "C", "C", "C", "C", "C"),
    ("EB-5-Set-Aside-Infrastructure", "C", "C", "C", "C", "C"),
]

# Family-Based Final Action Dates - August 2026
aug_fb_fa = [
    ("F1", "12-15-18", "12-15-18", "12-15-18", "12-01-07", "5-01-13"),
    ("F2A", "7-22-26", "7-22-26", "7-22-26", "7-22-25", "7-22-26"),
    ("F2B", "1-01-18", "1-01-18", "1-01-18", "2-15-09", "6-01-13"),
    ("F3", "5-15-12", "5-15-12", "5-15-12", "7-01-01", "2-22-06"),
    ("F4", "9-01-09", "9-01-09", "11-01-06", "4-08-01", "8-01-07"),
]

# Family-Based Filing Dates - August 2026
aug_fb_ff = [
    ("F1", "6-15-19", "6-15-19", "6-15-19", "12-01-08", "4-22-15"),
    ("F2A", "C", "C", "C", "C", "C"),
    ("F2B", "1-01-19", "1-01-19", "1-01-19", "5-15-10", "10-01-13"),
    ("F3", "3-01-13", "3-01-13", "3-01-13", "7-15-01", "8-08-06"),
    ("F4", "6-22-10", "6-22-10", "12-15-06", "4-30-01", "3-22-08"),
]


# Build all records
all_records = []

# July
all_records.extend(build_records(7, 2026, "employment", "final_action", july_eb_fa))
all_records.extend(build_records(7, 2026, "employment", "dates_for_filing", july_eb_ff))
all_records.extend(build_records(7, 2026, "family", "final_action", july_fb_fa))
all_records.extend(build_records(7, 2026, "family", "dates_for_filing", july_fb_ff))

# August
all_records.extend(build_records(8, 2026, "employment", "final_action", aug_eb_fa))
all_records.extend(build_records(8, 2026, "employment", "dates_for_filing", aug_eb_ff))
all_records.extend(build_records(8, 2026, "family", "final_action", aug_fb_fa))
all_records.extend(build_records(8, 2026, "family", "dates_for_filing", aug_fb_ff))

print(f"Total records to upsert: {len(all_records)}")

# Upsert in batches via curl
BATCH_SIZE = 50
inserted = 0
for i in range(0, len(all_records), BATCH_SIZE):
    batch = all_records[i:i + BATCH_SIZE]
    payload = json.dumps(batch)
    
    result = subprocess.run([
        "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}",
        "-X", "POST",
        f"{SUPABASE_URL}/rest/v1/visa_bulletin",
        "-H", f"apikey: {SUPABASE_KEY}",
        "-H", f"Authorization: Bearer {SUPABASE_KEY}",
        "-H", "Content-Type: application/json",
        "-H", "Prefer: resolution=merge-duplicates",
        "-d", payload,
    ], capture_output=True, text=True, timeout=30)
    
    code = result.stdout.strip()
    if code in ("200", "201"):
        inserted += len(batch)
        print(f"  ✅ Batch {i//BATCH_SIZE + 1}: {len(batch)} records (HTTP {code})")
    else:
        print(f"  ❌ Batch {i//BATCH_SIZE + 1}: HTTP {code}")
        # Try to get error body
        result2 = subprocess.run([
            "curl", "-s",
            "-X", "POST",
            f"{SUPABASE_URL}/rest/v1/visa_bulletin",
            "-H", f"apikey: {SUPABASE_KEY}",
            "-H", f"Authorization: Bearer {SUPABASE_KEY}",
            "-H", "Content-Type: application/json",
            "-H", "Prefer: resolution=merge-duplicates",
            "-d", payload,
        ], capture_output=True, text=True, timeout=30)
        print(f"     Error: {result2.stdout[:300]}")

print(f"\n✅ Total inserted: {inserted} records")
