#!/usr/bin/env python3
"""Seed the representatives table from the JSON data file."""
import json, os, subprocess, urllib.parse

DATA_FILE = os.path.join(os.path.dirname(__file__), "data", "indian-american-representatives.json")

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
ACCESS_TOKEN = os.environ["SUPABASE_ACCESS_TOKEN"]
PROJECT_REF = "lboecaekpynbpyijrbfz"
MGMT_URL = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"

# Sort order mapping: lower = higher on page
LEVEL_ORDER = {"federal": 0, "state": 1000, "local": 2000}
POSITION_ORDER = {
    "Vice President": 1,
    "Second Lady": 2,
    "Director of the Federal Bureau": 3,
    "U.S. Senator": 10,
    "U.S. Representative": 20,
    "Governor": 30,
    "Lieutenant Governor": 100,
    "State Senator": 200,
    "State Representative": 300,
    "State Assembly": 310,
    "State Delegate": 320,
    "Mayor": 400,
    "City Council": 500,
    "County": 550,
    "District Attorney": 560,
    "Judge": 570,
    "Chair": 580,
    "Commissioner": 590,
}

STATUS_ORDER = {"elected": 0, "appointed": 0, "candidate": 500, "former": 900}

def get_sort_order(rep):
    level = rep.get("level", "local")
    pos = rep.get("position", "")
    status = rep.get("status", "elected")
    
    base = LEVEL_ORDER.get(level, 2000)
    
    # Find best matching position
    pos_score = 999
    for key, score in POSITION_ORDER.items():
        if key.lower() in pos.lower():
            pos_score = min(pos_score, score)
    
    status_score = STATUS_ORDER.get(status, 0)
    
    return base + pos_score + status_score

def escape_sql(s):
    if s is None:
        return "NULL"
    return "'" + s.replace("'", "''") + "'"

def run_sql(query):
    payload = json.dumps({"query": query})
    result = subprocess.run(
        ["curl", "-s", "-X", "POST", MGMT_URL,
         "-H", f"Authorization: Bearer {ACCESS_TOKEN}",
         "-H", "Content-Type: application/json",
         "-d", payload],
        capture_output=True, text=True
    )
    return result.stdout

def main():
    with open(DATA_FILE) as f:
        data = json.load(f)
    
    reps = data["representatives"]
    print(f"Loaded {len(reps)} representatives")
    
    # Clear existing data
    print("Clearing existing data...")
    run_sql("DELETE FROM representatives;")
    
    # Insert in batches
    inserted = 0
    for rep in reps:
        sort_order = get_sort_order(rep)
        
        vals = ", ".join([
            escape_sql(rep.get("name")),
            escape_sql(rep.get("position")),
            escape_sql(rep.get("level")),
            escape_sql(rep.get("state")),
            escape_sql(rep.get("district")),
            escape_sql(rep.get("party")),
            escape_sql(rep.get("photo_url") or None),
            escape_sql(rep.get("website") or None),
            "NULL",  # wikipedia_url — to be filled later
            escape_sql(rep.get("twitter") or None),
            escape_sql(rep.get("bio")),
            escape_sql(rep.get("status", "elected")),
            escape_sql(rep.get("first_elected") or None),
            str(sort_order),
        ])
        
        sql = f"""INSERT INTO representatives 
            (name, position, level, state, district, party, photo_url, website, wikipedia_url, twitter, bio, status, first_elected, sort_order)
            VALUES ({vals});"""
        
        result = run_sql(sql)
        if "error" in result.lower() and "already exists" not in result.lower():
            print(f"  ERROR inserting {rep['name']}: {result[:200]}")
        else:
            inserted += 1
    
    print(f"\nInserted {inserted}/{len(reps)} representatives")
    
    # Verify
    result = run_sql("SELECT level, COUNT(*) as cnt FROM representatives GROUP BY level ORDER BY level;")
    print(f"Counts by level: {result}")

if __name__ == "__main__":
    main()
