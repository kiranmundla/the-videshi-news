#!/usr/bin/env python3
"""
Seed USCIS processing times and H-1B data into Supabase.
Data sourced from web search results (May 2026).
"""
import os, json, requests

SUPABASE_URL = "https://lboecaekpynbpyijrbfz.supabase.co"
SUPABASE_KEY = ""
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

def insert(table, records):
    url = f"{SUPABASE_URL}/rest/v1/{table}"
    resp = requests.post(url, headers=HEADERS, json=records)
    if resp.status_code in (200, 201):
        print(f"  ✅ Inserted {len(records)} into {table}")
        return len(records)
    else:
        print(f"  ❌ {table} error: {resp.status_code} {resp.text[:300]}")
        return 0

# ════════════════════════════════════════════════
# USCIS Processing Times (as of May 2026)
# ════════════════════════════════════════════════
# Sources: manifestlaw.com, usvisastack.ai, alonsoandalonsolaw.com, immigrationdirect.com

processing_times = [
    # I-140 Immigrant Petition for Alien Workers
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-1A (Extraordinary Ability)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 6.0, "estimated_range_low": 3.0, "estimated_range_high": 8.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-1A (Extraordinary Ability)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 7.0, "estimated_range_low": 4.0, "estimated_range_high": 10.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-1B (Outstanding Researcher)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 7.0, "estimated_range_low": 4.0, "estimated_range_high": 9.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-1B (Outstanding Researcher)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 8.0, "estimated_range_low": 5.0, "estimated_range_high": 11.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-2 (Advanced Degree)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 8.0, "estimated_range_low": 5.0, "estimated_range_high": 12.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-2 (Advanced Degree)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 10.0, "estimated_range_low": 6.0, "estimated_range_high": 14.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-2 NIW (National Interest Waiver)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 9.0, "estimated_range_low": 6.0, "estimated_range_high": 12.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-2 NIW (National Interest Waiver)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 11.0, "estimated_range_low": 7.0, "estimated_range_high": 15.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-3 (Skilled Workers)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 9.0, "estimated_range_low": 5.0, "estimated_range_high": 13.0},
    {"form_number": "I-140", "form_name": "Immigrant Petition for Alien Workers", "form_category": "EB-3 (Skilled Workers)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 12.0, "estimated_range_low": 7.0, "estimated_range_high": 17.0},

    # I-485 Adjustment of Status
    {"form_number": "I-485", "form_name": "Adjustment of Status", "form_category": "Employment-Based", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 14.0, "estimated_range_low": 8.0, "estimated_range_high": 20.0},
    {"form_number": "I-485", "form_name": "Adjustment of Status", "form_category": "Employment-Based", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 16.0, "estimated_range_low": 10.0, "estimated_range_high": 24.0},
    {"form_number": "I-485", "form_name": "Adjustment of Status", "form_category": "Family-Based", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 12.0, "estimated_range_low": 8.0, "estimated_range_high": 18.5},
    {"form_number": "I-485", "form_name": "Adjustment of Status", "form_category": "Family-Based", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 14.0, "estimated_range_low": 9.0, "estimated_range_high": 20.0},

    # I-765 Employment Authorization Document (EAD)
    {"form_number": "I-765", "form_name": "Employment Authorization Document (EAD)", "form_category": "Based on Pending I-485", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 4.5, "estimated_range_low": 3.0, "estimated_range_high": 7.0},
    {"form_number": "I-765", "form_name": "Employment Authorization Document (EAD)", "form_category": "Based on Pending I-485", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 5.0, "estimated_range_low": 3.0, "estimated_range_high": 7.0},
    {"form_number": "I-765", "form_name": "Employment Authorization Document (EAD)", "form_category": "H-4 Dependent", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 5.5, "estimated_range_low": 3.5, "estimated_range_high": 7.0},
    {"form_number": "I-765", "form_name": "Employment Authorization Document (EAD)", "form_category": "H-4 Dependent", "office": "Vermont Service Center", "office_code": "VSC", "processing_time_months": 6.0, "estimated_range_low": 4.0, "estimated_range_high": 7.0},

    # I-131 Advance Parole / Travel Document
    {"form_number": "I-131", "form_name": "Advance Parole / Travel Document", "form_category": "Based on Pending I-485", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 5.0, "estimated_range_low": 3.0, "estimated_range_high": 8.0},
    {"form_number": "I-131", "form_name": "Advance Parole / Travel Document", "form_category": "Based on Pending I-485", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 6.0, "estimated_range_low": 3.5, "estimated_range_high": 10.0},
    {"form_number": "I-131", "form_name": "Advance Parole / Travel Document", "form_category": "Humanitarian", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 8.0, "estimated_range_low": 4.0, "estimated_range_high": 12.0},

    # N-400 Naturalization / Citizenship
    {"form_number": "N-400", "form_name": "Application for Naturalization", "form_category": "5-Year Rule", "office": "National Average", "office_code": "NAT", "processing_time_months": 10.0, "estimated_range_low": 6.5, "estimated_range_high": 14.0},
    {"form_number": "N-400", "form_name": "Application for Naturalization", "form_category": "3-Year Rule (Married to USC)", "office": "National Average", "office_code": "NAT", "processing_time_months": 9.0, "estimated_range_low": 6.5, "estimated_range_high": 12.0},

    # I-130 Petition for Alien Relative
    {"form_number": "I-130", "form_name": "Petition for Alien Relative", "form_category": "Immediate Relative (IR)", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 10.0, "estimated_range_low": 5.0, "estimated_range_high": 15.0},
    {"form_number": "I-130", "form_name": "Petition for Alien Relative", "form_category": "Immediate Relative (IR)", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 12.0, "estimated_range_low": 6.0, "estimated_range_high": 18.0},
    {"form_number": "I-130", "form_name": "Petition for Alien Relative", "form_category": "Family Preference", "office": "Nebraska Service Center", "office_code": "NSC", "processing_time_months": 18.0, "estimated_range_low": 12.0, "estimated_range_high": 30.0},
    {"form_number": "I-130", "form_name": "Petition for Alien Relative", "form_category": "Family Preference", "office": "Texas Service Center", "office_code": "TSC", "processing_time_months": 22.0, "estimated_range_low": 14.0, "estimated_range_high": 36.0},

    # I-539 Change/Extend Nonimmigrant Status
    {"form_number": "I-539", "form_name": "Extend/Change Nonimmigrant Status", "form_category": "H-4 Extension", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 8.0, "estimated_range_low": 5.0, "estimated_range_high": 12.0},
    {"form_number": "I-539", "form_name": "Extend/Change Nonimmigrant Status", "form_category": "B-1/B-2 Extension", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 10.0, "estimated_range_low": 6.0, "estimated_range_high": 14.0},

    # I-129 H-1B Petition
    {"form_number": "I-129", "form_name": "Petition for Nonimmigrant Worker", "form_category": "H-1B (Cap-Subject)", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 4.0, "estimated_range_low": 2.0, "estimated_range_high": 6.0},
    {"form_number": "I-129", "form_name": "Petition for Nonimmigrant Worker", "form_category": "H-1B (Cap-Subject)", "office": "Vermont Service Center", "office_code": "VSC", "processing_time_months": 5.0, "estimated_range_low": 3.0, "estimated_range_high": 7.0},
    {"form_number": "I-129", "form_name": "Petition for Nonimmigrant Worker", "form_category": "H-1B (Extension/Transfer)", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 3.5, "estimated_range_low": 2.0, "estimated_range_high": 5.0},
    {"form_number": "I-129", "form_name": "Petition for Nonimmigrant Worker", "form_category": "L-1", "office": "California Service Center", "office_code": "CSC", "processing_time_months": 4.0, "estimated_range_low": 2.5, "estimated_range_high": 6.0},
    {"form_number": "I-129", "form_name": "Petition for Nonimmigrant Worker", "form_category": "L-1", "office": "Vermont Service Center", "office_code": "VSC", "processing_time_months": 5.0, "estimated_range_low": 3.0, "estimated_range_high": 7.0},
]

print("═" * 50)
print("SEEDING USCIS PROCESSING TIMES")
print("═" * 50)
insert("uscis_processing_times", processing_times)


# ════════════════════════════════════════════════
# H-1B Data
# ════════════════════════════════════════════════
# Sources: USCIS.gov, devdiscourse.com, theregister.com, tryalma.com

h1b_data = [
    # FY 2025 (pre-reform year)
    {"fiscal_year": 2025, "metric": "total_registrations", "value": "470342", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "unique_beneficiaries", "value": "442000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "selected", "value": "136399", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "selection_rate", "value": "29%", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "cap_regular", "value": "65000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "cap_masters", "value": "20000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2025, "metric": "india_pct", "value": "~72%", "source_url": "https://tryalma.com"},
    {"fiscal_year": 2025, "metric": "denial_rate", "value": "2-3%", "source_url": "https://tryalma.com"},

    # FY 2026 (beneficiary-centric, post-reform)
    {"fiscal_year": 2026, "metric": "total_registrations", "value": "343981", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "unique_beneficiaries", "value": "336153", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "selected", "value": "120141", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "selection_rate", "value": "35.3%", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "cap_regular", "value": "65000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "cap_masters", "value": "20000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2026, "metric": "india_pct", "value": "71%", "source_url": "https://tryalma.com"},
    {"fiscal_year": 2026, "metric": "masters_pct", "value": "57%", "source_url": "https://tryalma.com"},
    {"fiscal_year": 2026, "metric": "avg_registrations_per_beneficiary", "value": "1.01", "source_url": "https://ogletree.com"},
    {"fiscal_year": 2026, "metric": "duplicate_registrations", "value": "7828", "source_url": "https://medium.com"},
    {"fiscal_year": 2026, "metric": "processing_time_without_premium", "value": "5-7 months", "source_url": "https://tryalma.com"},
    {"fiscal_year": 2026, "metric": "computer_occupations_pct", "value": "64%", "source_url": "https://tryalma.com"},

    # FY 2027 (wage-weighted selection introduced)
    {"fiscal_year": 2027, "metric": "total_registrations", "value": "211600", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "registration_drop_pct", "value": "38.5%", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "selection_method", "value": "Wage-weighted (introduced FY2027)", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "masters_or_higher_pct", "value": "71.5%", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "lowest_wage_category_pct", "value": "17.7%", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "cap_regular", "value": "65000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "cap_masters", "value": "20000", "source_url": "https://uscis.gov"},
    {"fiscal_year": 2027, "metric": "new_fee_consular", "value": "$100,000 (for certain petitions)", "source_url": "https://constangy.com"},
    {"fiscal_year": 2027, "metric": "filing_period_start", "value": "April 1, 2026", "source_url": "https://uscis.gov"},
]

print("\n" + "═" * 50)
print("SEEDING H-1B DATA")
print("═" * 50)

# Use upsert for h1b_data (has unique constraint)
h1b_headers = {**HEADERS, "Prefer": "resolution=merge-duplicates"}
url = f"{SUPABASE_URL}/rest/v1/h1b_data"
resp = requests.post(url, headers=h1b_headers, json=h1b_data)
if resp.status_code in (200, 201):
    print(f"  ✅ Inserted {len(h1b_data)} H-1B data records")
else:
    print(f"  ❌ h1b_data error: {resp.status_code} {resp.text[:300]}")

print("\n✅ Seeding complete!")
