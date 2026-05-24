#!/usr/bin/env python3
"""Scrape additional historical visa bulletins (Jul-Dec 2025) for movement charts."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Import from the main scraper
from importlib.machinery import SourceFileLoader
scraper = SourceFileLoader("vb", os.path.join(os.path.dirname(__file__), "scrape-visa-bulletin.py")).load_module()

# Override the base URL to handle FY2025 bulletins (which are under /2025/)
bulletins = [
    (2025, 10), (2025, 11), (2025, 12),
]

grand_total = 0
for year, month in bulletins:
    print(f"\n{'='*60}")
    print(f"Scraping Visa Bulletin: {scraper.MONTH_NAMES[month].title()} {year}")
    print(f"{'='*60}")
    
    records = scraper.scrape_bulletin(year, month)
    if records:
        inserted = scraper.upsert_records(records)
        grand_total += inserted
        print(f"  ✅ Inserted {inserted} records for {scraper.MONTH_NAMES[month].title()} {year}")
    else:
        print(f"  ⚠️  No records scraped for {scraper.MONTH_NAMES[month].title()} {year}")

print(f"\n{'='*60}")
print(f"TOTAL: {grand_total} additional visa bulletin records")
print(f"{'='*60}")
