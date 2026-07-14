#!/usr/bin/env python3
"""Seed the diaspora_leaders table from the two JSON data files."""
import json, os, subprocess, urllib.parse

# Load env
env = {}
with open(os.path.expanduser('~/workspace/.env.supabase')) as f:
    for line in f:
        line = line.strip()
        if '=' in line and not line.startswith('#'):
            k, v = line.split('=', 1)
            env[k] = v

SUPABASE_URL = env['SUPABASE_URL']
SERVICE_KEY = env['SUPABASE_SERVICE_ROLE_KEY']
API_BASE = f"{SUPABASE_URL}/rest/v1"

def supabase_insert(table, rows):
    """Insert rows via PostgREST, batch of 50."""
    for i in range(0, len(rows), 50):
        batch = rows[i:i+50]
        payload = json.dumps(batch)
        result = subprocess.run([
            'curl', '-sS', '-X', 'POST',
            f'{API_BASE}/{table}',
            '-H', f'Authorization: Bearer {SERVICE_KEY}',
            '-H', f'apikey: {SERVICE_KEY}',
            '-H', 'Content-Type: application/json',
            '-H', 'Prefer: return=minimal',
            '-d', payload
        ], capture_output=True, text=True)
        if result.returncode != 0 or ('error' in result.stdout.lower() and 'code' in result.stdout.lower()):
            print(f"Error inserting batch {i//50}: {result.stdout[:500]}")
        else:
            print(f"Inserted batch {i//50} ({len(batch)} rows)")

# Subcategory assignment for reps (government)
def assign_govt_subcategory(rep):
    level = rep.get('level', 'federal')
    if level == 'federal':
        return 'Federal'
    elif level == 'state':
        return 'State'
    elif level == 'local':
        return 'Local'
    return 'Federal'

# Subcategory assignment for leaders
def assign_leader_subcategory(leader):
    cat = leader.get('category', '')
    pos = (leader.get('position', '') or '').lower()
    company = (leader.get('company', '') or '').lower()
    name = leader.get('name', '')
    
    if cat == 'government':
        country = leader.get('country', 'US')
        if country == 'US':
            return 'Federal'
        return 'International'
    
    elif cat == 'tech_business':
        if 'ceo' in pos or 'chairman' in pos:
            return 'CEO'
        elif 'founder' in pos or 'co-founder' in pos or 'venture' in pos or 'investor' in pos or 'vc' in pos.split():
            return 'Founder & VC'
        else:
            return 'Senior Executive'
    
    elif cat == 'arts_entertainment':
        if any(w in pos for w in ['director', 'producer', 'actor', 'actress', 'screenwriter', 'filmmaker']):
            return 'Film & TV'
        elif any(w in pos for w in ['comedian', 'host', 'tv host', 'journalist', 'anchor']):
            return 'Comedy & Media'
        elif any(w in pos for w in ['musician', 'singer', 'composer', 'conductor']):
            return 'Music'
        elif any(w in pos for w in ['author', 'writer', 'novelist', 'poet']):
            return 'Writing & Literature'
        return 'Film & TV'  # default
    
    elif cat == 'science_medicine':
        if 'astronaut' in pos:
            return 'Space & Aviation'
        elif 'nobel' in pos:
            return 'Nobel Laureate'
        return 'Research & Medicine'
    
    elif cat == 'academia':
        if 'nobel' in pos.lower():
            return 'Nobel Laureate'
        elif 'president' in pos or 'dean' in pos or 'chancellor' in pos:
            return 'University Leader'
        elif 'professor' in pos:
            return 'Professor'
        return 'Academic'
    
    return None

# Sort order: lower = higher priority
CATEGORY_ORDER = {'government': 0, 'tech_business': 1, 'arts_entertainment': 2, 'science_academia': 3}
GOVT_SUBCAT_ORDER = {'Federal': 0, 'International': 1, 'State': 2, 'Local': 3}
TECH_SUBCAT_ORDER = {'CEO': 0, 'Founder & VC': 1, 'Senior Executive': 2}

def compute_sort_order(entry):
    cat = entry.get('category', '')
    subcat = entry.get('subcategory', '')
    cat_ord = CATEGORY_ORDER.get(cat, 9) * 10000
    
    if cat == 'government':
        sub_ord = GOVT_SUBCAT_ORDER.get(subcat, 5) * 100
    elif cat == 'tech_business':
        sub_ord = TECH_SUBCAT_ORDER.get(subcat, 5) * 100
    else:
        sub_ord = 0
    
    return cat_ord + sub_ord

# ------- MAIN -------

# Load reps
with open(os.path.expanduser('~/workspace/the-videshi-news/pipeline/data/indian-american-representatives.json')) as f:
    reps_data = json.load(f)['representatives']

# Load leaders
with open(os.path.expanduser('~/workspace/the-videshi-news/pipeline/data/indian-american-leaders.json')) as f:
    leaders_data = json.load(f)['leaders']

all_rows = []
seen_names = set()

# Process reps first (US government)
for rep in reps_data:
    name = rep['name']
    if name in seen_names:
        continue
    seen_names.add(name)
    
    subcat = assign_govt_subcategory(rep)
    row = {
        'name': name,
        'position': rep.get('position', ''),
        'category': 'government',
        'subcategory': subcat,
        'country': 'US',
        'state': rep.get('state'),
        'district': rep.get('district'),
        'company': None,
        'party': rep.get('party'),
        'photo_url': rep.get('photo_url') or None,
        'website': rep.get('website') or None,
        'wikipedia_url': None,
        'twitter': rep.get('twitter') or None,
        'bio': rep.get('bio') or None,
        'notable_achievement': None,
        'status': rep.get('status', 'active'),
    }
    row['sort_order'] = compute_sort_order(row)
    all_rows.append(row)

# Process leaders
for leader in leaders_data:
    name = leader['name']
    if name in seen_names:
        continue
    seen_names.add(name)
    
    cat = leader.get('category', 'tech_business')
    # Map academia and science_medicine to science_academia
    if cat in ('academia', 'science_medicine'):
        cat = 'science_academia'
    
    subcat = assign_leader_subcategory(leader)
    country = leader.get('country', 'US')
    
    row = {
        'name': name,
        'position': leader.get('position', ''),
        'category': cat,
        'subcategory': subcat,
        'country': country,
        'state': None,
        'district': None,
        'company': leader.get('company') or None,
        'party': None,
        'photo_url': leader.get('photo_url') or None,
        'website': leader.get('website') or None,
        'wikipedia_url': leader.get('wikipedia_url') or None,
        'twitter': leader.get('twitter') or None,
        'bio': leader.get('bio') or None,
        'notable_achievement': leader.get('notable_achievement') or None,
        'status': 'active',
    }
    row['sort_order'] = compute_sort_order(row)
    all_rows.append(row)

print(f"\nTotal rows to insert: {len(all_rows)}")
cats = {}
for r in all_rows:
    key = f"{r['category']}/{r['subcategory']}"
    cats[key] = cats.get(key, 0) + 1
for k in sorted(cats):
    print(f"  {k}: {cats[k]}")

countries = {}
for r in all_rows:
    c = r['country']
    countries[c] = countries.get(c, 0) + 1
print(f"\nCountries: {len(countries)}")
for c in sorted(countries, key=lambda x: -countries[x]):
    print(f"  {c}: {countries[c]}")

# Clean up None values for JSON
for row in all_rows:
    for k, v in list(row.items()):
        if v is None:
            del row[k]

# Insert
supabase_insert('diaspora_leaders', all_rows)
print("\nDone!")
