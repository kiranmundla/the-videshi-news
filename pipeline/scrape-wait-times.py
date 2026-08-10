#!/usr/bin/env python3
"""
Scrape US State Dept Global Visa Wait Times for India + third-country consulates.
Updates consulate_wait_times table in Supabase.
Source: travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html
This page is public, no authentication needed, updated monthly by State Dept.
"""
import argparse
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone

try:
    import requests as _requests
except ImportError:
    _requests = None

TARGETS = {
    # India consulates
    "Chennai (Madras)": ("chennai", "Chennai"),
    "Hyderabad": ("hyderabad", "Hyderabad"),
    "Kolkata": ("kolkata", "Kolkata"),
    "Mumbai (Bombay)": ("mumbai", "Mumbai"),
    "New Delhi": ("new_delhi", "New Delhi"),
    # Third-country options for Indian H-1B holders
    "Dubai": ("dubai", "Dubai (UAE)"),
    "Singapore": ("singapore", "Singapore"),
    "Toronto": ("toronto", "Toronto (Canada)"),
    "Calgary": ("calgary", "Calgary (Canada)"),
    "London": ("london", "London (UK)"),
}

VISA_TYPE_DISPLAY = {
    "B1B2": "Visitor (B1/B2)",
    "F_M_J": "Student (F/M/J)",
    "H_L_O_P_Q": "Work (H/L/O/P/Q)",
    "C_D": "Crew/Transit (C/D)",
}

VISA_COLS = ["B1B2", "B1B2_next", "F_M_J", "H_L_O_P_Q", "C_D"]

def load_env(path):
    if not os.path.exists(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                os.environ[key.strip()] = val.strip().strip('"').strip("'")

def parse_months(text):
    """Convert '7.5 Months' or '< 0.5 Month' to float, or None for NA."""
    text = text.strip()
    if text == "NA" or not text:
        return None
    m = re.search(r'([\d.]+)\s*Month', text)
    if m:
        return float(m.group(1))
    return None

def fetch_wait_times(html_file=None):
    """Fetch and parse the State Dept wait times page.
    
    If html_file is provided, reads HTML from that file instead of fetching.
    This is the preferred path since travel.state.gov is IP-blocked from this server.
    """
    if html_file:
        print(f"Reading HTML from {html_file}")
        with open(html_file, "r") as f:
            html = f.read()
    else:
        url = "https://travel.state.gov/content/travel/en/us-visas/visa-information-resources/global-visa-wait-times.html"
        # travel.state.gov blocks requests/urllib from this server (IP-blocked, returns 403).
        # Use curl with a browser-like UA as primary, fall back to requests/urllib.
        import subprocess as _sp
        try:
            cp = _sp.run(
                ["curl", "-sL", "-A",
                 "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36",
                 "--max-time", "30", url],
                capture_output=True, text=True, timeout=45)
            if cp.returncode == 0 and len(cp.stdout) > 1000:
                html = cp.stdout
            else:
                raise RuntimeError(f"curl failed rc={cp.returncode} len={len(cp.stdout)}")
        except Exception as curl_err:
            print(f"curl fetch failed ({curl_err}), trying requests...")
            headers = {"User-Agent": "TheVideshi/1.0 (immigration news)"}
            if _requests:
                r = _requests.get(url, headers=headers, timeout=30)
                r.raise_for_status()
                html = r.text
            else:
                req = urllib.request.Request(url, headers=headers)
                with urllib.request.urlopen(req, timeout=30) as resp:
                    html = resp.read().decode("utf-8")
    
    results = []
    now = datetime.now(timezone.utc).isoformat()
    
    # Parse table rows - look for target cities
    # The page has a big HTML table; we extract rows matching our target cities
    # Simple regex approach since the table structure is consistent
    
    # Find all table rows
    row_pattern = re.compile(r'<tr[^>]*>(.*?)</tr>', re.DOTALL)
    cell_pattern = re.compile(r'<td[^>]*>(.*?)</td>', re.DOTALL)
    
    for row_match in row_pattern.finditer(html):
        row_html = row_match.group(1)
        cells = cell_pattern.findall(row_html)
        if len(cells) < 6:
            continue
        
        # Clean HTML from cells
        city_raw = re.sub(r'<[^>]+>', '', cells[0]).strip()
        
        # Check if this city is one we care about
        slug = None
        display = None
        for target_name, (target_slug, target_display) in TARGETS.items():
            if target_name.lower() in city_raw.lower():
                slug = target_slug
                display = target_display
                break
        
        if not slug:
            continue
        
        avg_b1b2 = parse_months(re.sub(r'<[^>]+>', '', cells[1]).strip())
        next_b1b2 = parse_months(re.sub(r'<[^>]+>', '', cells[2]).strip())
        next_fmj = parse_months(re.sub(r'<[^>]+>', '', cells[3]).strip())
        next_hlop = parse_months(re.sub(r'<[^>]+>', '', cells[4]).strip())
        next_cd = parse_months(re.sub(r'<[^>]+>', '', cells[5]).strip())
        
        # Insert one row per visa type
        for visa_type, val in [
            ("B1B2", next_b1b2),
            ("F_M_J", next_fmj),
            ("H_L_O_P_Q", next_hlop),
            ("C_D", next_cd),
        ]:
            results.append({
                "consulate": slug,
                "consulate_display": display,
                "visa_type": visa_type,
                "visa_type_display": VISA_TYPE_DISPLAY.get(visa_type, visa_type),
                "avg_wait_months": avg_b1b2 if visa_type == "B1B2" else None,
                "next_available_months": val,
                "scraped_at": now,
            })
        
        print(f"  {slug}: B1/B2={next_b1b2}mo, F/M/J={next_fmj}mo, H/L/O/P={next_hlop}mo, C/D={next_cd}mo")
    
    return results

def upsert_to_supabase(rows):
    """Insert new wait time rows into Supabase."""
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/consulate_wait_times"
    payload = json.dumps(rows).encode()
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"],
        "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    })
    try:
        with urllib.request.urlopen(req) as resp:
            print(f"Inserted {len(rows)} wait time rows")
            return True
    except Exception as e:
        print(f"Supabase insert error: {e}")
        # Try reading the error body
        if hasattr(e, 'read'):
            print(f"  Response: {e.read().decode()}")
        return False

def update_static_json(rows):
    """Write latest wait times to static JSON for frontend."""
    repo = os.path.expanduser("~/workspace/the-videshi-news")
    out = os.path.join(repo, "public/data/visa-wait-times.json")
    with open(out, "w") as f:
        json.dump(rows, f, indent=2)
        f.write("\n")
    print(f"Wrote {len(rows)} rows to visa-wait-times.json")

def main():
    parser = argparse.ArgumentParser(description="Scrape US State Dept visa wait times")
    parser.add_argument("--html-file", help="Path to pre-fetched HTML file (skips direct fetch)")
    args = parser.parse_args()

    load_env(os.path.expanduser("~/workspace/.env.supabase"))
    
    print("Fetching State Dept wait times...")
    rows = fetch_wait_times(html_file=args.html_file)
    
    if not rows:
        print("ERROR: No rows parsed. Page structure may have changed.")
        return
    
    print(f"\nParsed {len(rows)} wait time entries for {len(set(r['consulate'] for r in rows))} consulates")
    
    # Upsert to Supabase
    upsert_to_supabase(rows)
    
    # Update static JSON
    update_static_json(rows)
    
    # Git push
    load_env(os.path.expanduser("~/workspace/.env.github"))
    repo = os.path.expanduser("~/workspace/the-videshi-news")
    os.chdir(repo)
    import subprocess
    result = subprocess.run(["git", "diff", "--name-only", "public/data/visa-wait-times.json"],
                          capture_output=True, text=True)
    if "visa-wait-times.json" in result.stdout:
        subprocess.run(["git", "add", "public/data/visa-wait-times.json"], check=True)
        subprocess.run(["git", "commit", "-m", f"update wait times {datetime.now().strftime('%Y-%m-%d')}"], check=True)
        subprocess.run(["git", "push", "origin", "main"], check=True)
        print("Pushed updated wait times")
    else:
        print("No changes to wait times")

if __name__ == "__main__":
    main()
