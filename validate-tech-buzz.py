#!/usr/bin/env python3
"""Validate tech-buzz.json schema for The Videshi Power Pulse."""
import json, sys

REQUIRED_CATEGORIES = {"india": 12, "world": 11, "tech": 14, "sports": 15}

with open("/home/hatch/workspace/the-videshi-news/public/data/tech-buzz.json") as f:
    data = json.load(f)

errors = []

# Top-level keys
for key in ("leaders", "lastUpdated", "last_updated"):
    if key not in data:
        errors.append(f"Missing top-level key: {key}")

leaders = data.get("leaders", [])
if not isinstance(leaders, list):
    errors.append("'leaders' is not a list")
    print("\n".join(errors))
    sys.exit(1)

print(f"Total leaders: {len(leaders)}")
if len(leaders) != 52:
    errors.append(f"Expected 52 leaders, got {len(leaders)}")

# Check category counts
cat_counts = {}
for l in leaders:
    cat = l.get("category", "MISSING")
    cat_counts[cat] = cat_counts.get(cat, 0) + 1
print(f"Category counts: {cat_counts}")
for cat, expected in REQUIRED_CATEGORIES.items():
    actual = cat_counts.get(cat, 0)
    if actual != expected:
        errors.append(f"Category '{cat}': expected {expected}, got {actual}")

# Check each leader
for i, leader in enumerate(leaders):
    name = leader.get("name", f"leader[{i}]")
    
    # Required fields
    for field in ("name", "handle", "category", "platform", "posts"):
        if field not in leader:
            errors.append(f"{name}: missing field '{field}'")
    
    # Platform must be "x"
    if leader.get("platform") != "x":
        errors.append(f"{name}: platform is '{leader.get('platform')}', expected 'x'")
    
    # Posts must be a non-empty array
    posts = leader.get("posts", [])
    if not isinstance(posts, list) or len(posts) == 0:
        errors.append(f"{name}: 'posts' must be a non-empty array")
        continue
    
    for j, post in enumerate(posts):
        prefix = f"{name}.posts[{j}]"
        
        # Required post fields
        for field in ("text", "caption", "url", "thumbnail", "timestamp"):
            if field not in post:
                errors.append(f"{prefix}: missing '{field}'")
        
        # text and caption must match
        if post.get("text") != post.get("caption"):
            errors.append(f"{prefix}: 'text' and 'caption' differ")
        
        # text must not be empty
        if not post.get("text", "").strip():
            errors.append(f"{prefix}: 'text' is empty")
        
        # url must point to x.com
        url = post.get("url", "")
        if not url.startswith("https://x.com/"):
            errors.append(f"{prefix}: url '{url}' does not start with https://x.com/")
        
        # thumbnail must be empty string
        if post.get("thumbnail") != "":
            errors.append(f"{prefix}: thumbnail should be empty string, got '{post.get('thumbnail')}'")
        
        # Check first-person voice (basic: should not start with "He ", "She ", "They ", or leader's name)
        text = post.get("text", "")
        third_person_starts = [f"{name} ", "He ", "She ", "They "]
        for tp in third_person_starts:
            if text.startswith(tp):
                errors.append(f"{prefix}: text appears third-person (starts with '{tp.strip()}')")

# Print results
if errors:
    print(f"\n❌ VALIDATION FAILED — {len(errors)} error(s):")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)
else:
    print("\n✅ VALIDATION PASSED — all 52 leaders, schema correct, first-person voice")
    sys.exit(0)
