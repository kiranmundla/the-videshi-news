#!/usr/bin/env python3
"""
enrich-directory.py — AI-enrich directory listings with diaspora-specific metadata.

Adds: languages, community, tags, ai_description.
Uses GPT-4o-mini for cost efficiency. Processes in batches.

Usage:
  python3 pipeline/enrich-directory.py [--limit N] [--dry-run] [--category "Attorneys & Immigration"]
"""

import os, sys, json, time, argparse, re
from datetime import datetime, timezone

# ── env ──────────────────────────────────────────────────────────────────────
for ef in [
    os.path.expanduser("~/workspace/.env.supabase"),
    os.path.expanduser("~/workspace/.env.openai"),
]:
    if os.path.isfile(ef):
        with open(ef) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip())

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]

import subprocess

# ── Supabase helpers ─────────────────────────────────────────────────────────
def sb_get(table, params=""):
    url = f"{SUPABASE_URL}/rest/v1/{table}?{params}"
    r = subprocess.run(
        ["curl", "-sS", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Accept: application/json"],
        capture_output=True, text=True
    )
    return json.loads(r.stdout)

def sb_patch(table, row_id, data):
    url = f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{row_id}"
    payload = json.dumps(data)
    r = subprocess.run(
        ["curl", "-sS", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True
    )
    return r.returncode == 0 and "error" not in r.stdout.lower()


# ── GPT helper ───────────────────────────────────────────────────────────────
def call_gpt(prompt, system_prompt, max_retries=3):
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ],
    })
    for attempt in range(max_retries):
        r = subprocess.run(
            ["curl", "-sS", "--max-time", "30",
             "https://api.openai.com/v1/chat/completions",
             "-H", f"Authorization: Bearer {OPENAI_API_KEY}",
             "-H", "Content-Type: application/json",
             "-d", payload],
            capture_output=True, text=True
        )
        if not r.stdout.strip():
            wait = 2 ** (attempt + 1)
            print(f"  ⚠ Empty response (attempt {attempt+1}/{max_retries}), retrying in {wait}s...", flush=True)
            time.sleep(wait)
            continue
        try:
            resp = json.loads(r.stdout)
            if "error" in resp:
                err_msg = resp["error"].get("message", "")
                err_type = resp["error"].get("type", "")
                if "rate_limit" in err_type or "429" in err_msg or "quota" in err_msg.lower():
                    wait = 2 ** (attempt + 1)
                    print(f"  ⚠ Rate limited (attempt {attempt+1}/{max_retries}), retrying in {wait}s...", flush=True)
                    time.sleep(wait)
                    continue
                print(f"  ⚠ API error: {err_type}: {err_msg}", flush=True)
                return None
            content = resp["choices"][0]["message"]["content"]
            return json.loads(content)
        except Exception as e:
            wait = 2 ** (attempt + 1)
            print(f"  ⚠ GPT parse error (attempt {attempt+1}/{max_retries}): {e}", flush=True)
            if attempt < max_retries - 1:
                time.sleep(wait)
    print(f"  ⚠ GPT call failed after {max_retries} attempts", flush=True)
    return None


# ── Enrichment prompt ────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are an expert on the Indian diaspora in the United States.
You enrich business directory listings with metadata relevant to Indian/South Asian Americans.

Given a business listing (name, category, subcategory, city, state, description), return JSON:
{
  "languages": ["Hindi", "English", ...],
  "community": "South Indian" | "North Indian" | "Gujarati" | "Punjabi" | "Bengali" | "Telugu" | "Tamil" | "Marathi" | "Malayali" | "Kannada" | "Pan-Indian" | "South Asian" | null,
  "tags": ["tag1", "tag2", ...],
  "ai_description": "1-2 sentence description tailored to Indian diaspora audience"
}

Rules:
- "languages": Infer from the business name, type, and location. Most Indian businesses speak English + at least one Indian language. Be conservative — only list languages you're fairly confident about. Always include "English" for US businesses.
- "community": The regional Indian community this business primarily serves. Use "Pan-Indian" if it serves all. Use null if you can't determine or it's not clearly Indian-specific.
- "tags": 3-8 short, specific tags relevant to the Indian diaspora. Examples by category:
  - Attorneys: "H-1B visa", "green card", "immigration law", "business visa", "family-based immigration"
  - Doctors: "accepts most insurance", "Telugu-speaking", "pediatrics", "Ayurvedic"  
  - Tax: "India-US dual filing", "FBAR/FATCA", "NRI tax planning", "business tax"
  - Restaurants/Catering: "South Indian", "vegetarian", "wedding catering", "tiffin service"
  - Religious: "Hindu temple", "puja services", "Sikh gurdwara", "weekend classes"
  - Real Estate: "NRI property", "first-time homebuyer", "investment property"
  - Education: "SAT prep", "Kumon", "Indian classical music", "Bharatanatyam"
  Use specific, searchable terms. Don't use generic tags like "professional" or "quality service".
- "ai_description": Write for an NRI audience. Highlight what makes this relevant to the Indian community. Keep it 1-2 sentences, factual, no hype.
- If the business doesn't seem Indian/South Asian specific at all, still tag it usefully but set community to null.
"""

def build_prompt(listing):
    parts = [f"Business: {listing['name']}"]
    parts.append(f"Category: {listing['category']}")
    if listing.get("subcategory"):
        parts.append(f"Subcategory: {listing['subcategory']}")
    parts.append(f"Location: {listing.get('city', '')}, {listing.get('state', '')}")
    if listing.get("description"):
        parts.append(f"Description: {listing['description']}")
    if listing.get("affiliation"):
        parts.append(f"Affiliation: {listing['affiliation']}")
    return "\n".join(parts)


# ── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=50)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--category", type=str, default=None)
    args = parser.parse_args()

    # Fetch un-enriched listings
    params = "enriched_at=is.null&order=created_at.asc&limit=" + str(args.limit)
    params += "&select=id,name,category,subcategory,city,state,description,affiliation"
    if args.category:
        from urllib.parse import quote
        params += f"&category=eq.{quote(args.category, safe='')}"

    listings = sb_get("directory_listings", params)
    print(f"📂 Found {len(listings)} un-enriched listings (limit={args.limit})")

    enriched = 0
    errors = 0
    for i, listing in enumerate(listings):
        print(f"\n[{i+1}/{len(listings)}] {listing['name']} ({listing['category']}, {listing.get('city','')} {listing.get('state','')})")

        prompt = build_prompt(listing)
        result = call_gpt(prompt, SYSTEM_PROMPT)

        if not result:
            errors += 1
            continue

        # Validate & clean
        languages = result.get("languages", ["English"])
        if not isinstance(languages, list):
            languages = ["English"]

        community = result.get("community")
        if community and not isinstance(community, str):
            community = None

        tags = result.get("tags", [])
        if not isinstance(tags, list):
            tags = []
        tags = [t for t in tags if isinstance(t, str) and len(t) > 1][:10]

        ai_desc = result.get("ai_description", "")
        if not isinstance(ai_desc, str):
            ai_desc = ""

        print(f"  Languages: {languages}")
        print(f"  Community: {community}")
        print(f"  Tags: {tags}")
        print(f"  Desc: {ai_desc[:80]}...")

        if not args.dry_run:
            ok = sb_patch("directory_listings", listing["id"], {
                "languages": json.dumps(languages),
                "tags": json.dumps(tags),
                "community": community,
                "ai_description": ai_desc,
                "enriched_at": datetime.now(timezone.utc).isoformat(),
            })
            if ok:
                enriched += 1
            else:
                print("  ⚠ PATCH failed")
                errors += 1
        else:
            enriched += 1

        # Rate limit — ~2 req/sec for mini (conservative to avoid proxy throttle)
        time.sleep(0.5)

    print(f"\n{'🧪 DRY RUN' if args.dry_run else '✅ DONE'}: {enriched} enriched, {errors} errors out of {len(listings)} listings")

if __name__ == "__main__":
    main()
