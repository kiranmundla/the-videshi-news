#!/usr/bin/env python3
"""Shared module: load social account data from the Supabase `social_accounts` table.

Replaces the old pattern of reading social-embed-registry.json.
All data is cached in-process after the first fetch.

Usage:
    from social_registry import load_registry, load_vvip_handles, load_company_handles, get_handle_name_map
    from social_registry import load_flat_entries, load_x_handle_set

Env: ~/workspace/.env.supabase  (SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
"""

import json, os, subprocess, sys
from collections import defaultdict

# ── Env ───────────────────────────────────────────────────────────────────────

def _load_env(path):
    if os.path.exists(path):
        with open(path) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    os.environ.setdefault(k.strip(), v.strip())

_load_env(os.path.expanduser("~/workspace/.env.supabase"))

# ── Raw DB fetch (curl, cached) ──────────────────────────────────────────────

_RAW_CACHE = None

def _fetch_all_rows():
    """Fetch all enabled rows from social_accounts via curl. Cached per-process."""
    global _RAW_CACHE
    if _RAW_CACHE is not None:
        return _RAW_CACHE

    sb_url = os.environ.get("SUPABASE_URL", "")
    sb_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not sb_url or not sb_key:
        print("  ⚠ social_registry: SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY not set", file=sys.stderr)
        _RAW_CACHE = []
        return _RAW_CACHE

    url = f"{sb_url}/rest/v1/social_accounts?enabled=eq.true&select=handle,platform,name,category,priority&limit=2000"
    try:
        result = subprocess.run(
            ["curl", "-sS", "--max-time", "15", url,
             "-H", f"apikey: {sb_key}",
             "-H", f"Authorization: Bearer {sb_key}"],
            capture_output=True, text=True, timeout=20,
        )
        rows = json.loads(result.stdout)
        if isinstance(rows, list):
            _RAW_CACHE = rows
        else:
            print(f"  ⚠ social_registry: unexpected response: {str(rows)[:200]}", file=sys.stderr)
            _RAW_CACHE = []
    except Exception as e:
        print(f"  ⚠ social_registry: fetch failed: {e}", file=sys.stderr)
        _RAW_CACHE = []

    return _RAW_CACHE


# ── Public API ────────────────────────────────────────────────────────────────

_REGISTRY_CACHE = None

def load_registry():
    """Return data in the same nested-dict format the old JSON had:

        {category: {"persons": [{name, x, instagram, threads, covers, ...}],
                     "organizations": [...]}}

    Since the DB doesn't distinguish person vs org, everything goes under
    "persons" — downstream matching logic doesn't depend on that split.
    Metadata keys (_description, _updated, _usage) are omitted.
    """
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is not None:
        return _REGISTRY_CACHE

    rows = _fetch_all_rows()

    # Group by (category, name) → collect platform handles
    # name can be empty for entries that were just handles
    entities = defaultdict(lambda: {"x": None, "instagram": None, "threads": None, "name": "", "category": ""})

    for row in rows:
        handle = row.get("handle", "")
        platform = row.get("platform", "twitter")
        name = row.get("name", "") or ""
        category = row.get("category", "") or ""

        # Entity key: combine name+category to group cross-platform handles
        # If name is empty, use handle as fallback key
        entity_key = (category, name.lower() if name else f"_handle_{handle.lower()}")

        ent = entities[entity_key]
        if name:
            ent["name"] = name   # prefer non-empty name
        elif not ent["name"]:
            ent["name"] = handle
        ent["category"] = category

        if platform == "twitter":
            ent["x"] = handle
        elif platform == "instagram":
            ent["instagram"] = handle
        elif platform == "threads":
            ent["threads"] = handle

    # Build registry dict
    registry = {}
    for (cat, _key), ent in entities.items():
        if cat not in registry:
            registry[cat] = {"persons": [], "organizations": []}
        registry[cat]["persons"].append(ent)

    _REGISTRY_CACHE = registry
    return registry


_VVIP_CACHE = None

def load_vvip_handles():
    """Return {category: [handle, ...]} for VVIP twitter handles."""
    global _VVIP_CACHE
    if _VVIP_CACHE is not None:
        return _VVIP_CACHE

    rows = _fetch_all_rows()
    result = defaultdict(list)
    for row in rows:
        if row.get("priority") == "vvip" and row.get("platform") == "twitter":
            result[row.get("category", "")].append(row["handle"])

    _VVIP_CACHE = dict(result)
    return _VVIP_CACHE


_COMPANY_CACHE = None

def load_company_handles():
    """Return set of lowercased twitter handles that are companies/orgs.

    The DB doesn't currently distinguish person vs org, so this returns an
    empty set for now. social-feed-cache.py's company filter is minor.
    """
    global _COMPANY_CACHE
    if _COMPANY_CACHE is not None:
        return _COMPANY_CACHE
    _COMPANY_CACHE = set()
    return _COMPANY_CACHE


_NAME_MAP_CACHE = {}

def get_handle_name_map(platform="twitter"):
    """Return {handle_lower: full_name} for the given platform."""
    if platform in _NAME_MAP_CACHE:
        return _NAME_MAP_CACHE[platform]

    rows = _fetch_all_rows()
    result = {}
    for row in rows:
        if row.get("platform") == platform:
            name = row.get("name") or ""
            if name:
                result[row["handle"].lower()] = name

    _NAME_MAP_CACHE[platform] = result
    return result


def load_flat_entries():
    """Return a flat list of dicts, each with:
        {name, handle, category, kind, x, threads, instagram}
    where `handle` = the first available handle (x > threads > ig).

    Used by shotstack-reel*.py for video handle allowlisting and matching.
    """
    registry = load_registry()
    out = []
    for cat, data in registry.items():
        if cat.startswith("_"):
            continue
        for kind in ("persons", "organizations"):
            for e in (data.get(kind) or []):
                if not isinstance(e, dict):
                    continue
                x = (e.get("x") or "").lstrip("@") or None
                threads = (e.get("threads") or "").lstrip("@") or None
                instagram = (e.get("instagram") or "").lstrip("@") or None
                if not (x or threads or instagram):
                    continue
                out.append({
                    "name": e.get("name", ""),
                    "handle": x or threads or instagram,
                    "category": cat,
                    "kind": kind,
                    "x": x,
                    "threads": threads,
                    "instagram": instagram,
                })
    return out


def load_x_handle_set():
    """Return a set of all lowercased X/twitter handles. Useful for allowlists."""
    rows = _fetch_all_rows()
    return {r["handle"].lower() for r in rows if r.get("platform") == "twitter"}


def collect_handles():
    """Return (sorted_x_handles, sorted_ig_handles) — all lowercased.
    
    Used by refresh-embed-cache.py.
    """
    rows = _fetch_all_rows()
    x_handles = set()
    ig_handles = set()
    for row in rows:
        h = row["handle"].lower()
        if row.get("platform") == "twitter":
            x_handles.add(h)
        elif row.get("platform") == "instagram":
            ig_handles.add(h)
    return sorted(x_handles), sorted(ig_handles)


def load_name_to_handles():
    """Return {name_lower: {name, instagram, x}} for person matching.
    
    Used by add-social-handles.py.
    """
    registry = load_registry()
    handles = {}
    for cat, data in registry.items():
        if not isinstance(data, dict):
            continue
        for person in data.get("persons", []):
            name = person.get("name", "")
            if name:
                handles[name.lower()] = {
                    "name": name,
                    "instagram": person.get("instagram"),
                    "x": person.get("x"),
                }
    return handles


def load_registry_names():
    """Return [(name, subject_type), ...] for media-library matching.
    
    subject_type is 'person' for persons, 'thing' for organizations.
    """
    registry = load_registry()
    names = []
    for cat, data in registry.items():
        if not isinstance(data, dict):
            continue
        for grp in ("persons", "organizations"):
            for e in data.get(grp, []):
                if e.get("name"):
                    st = "person" if grp == "persons" else "thing"
                    names.append((e["name"], st))
    return names


if __name__ == "__main__":
    r = load_registry()
    print(f"Categories: {list(r.keys())}")
    total = sum(len(v.get('persons', [])) for v in r.values())
    print(f"Total entries: {total}")
    v = load_vvip_handles()
    print(f"VVIP categories: {list(v.keys())}")
    print(f"VVIP total handles: {sum(len(h) for h in v.values())}")
    m = get_handle_name_map()
    print(f"Handle→name map size (twitter): {len(m)}")
    m2 = get_handle_name_map("instagram")
    print(f"Handle→name map size (instagram): {len(m2)}")
    x, ig = collect_handles()
    print(f"X handles: {len(x)}, IG handles: {len(ig)}")
    flat = load_flat_entries()
    print(f"Flat entries: {len(flat)}")
