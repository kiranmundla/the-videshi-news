#!/usr/bin/env python3
"""
Build unified movies.json for the homepage Movies rail.

Merges three sources:
1. now-in-theaters.json — what's playing (poster, theater info, trailer)
2. movie-reviews.json — our critic reviews (star rating, review link)
3. boxoffice.json — trade figures (India net, worldwide, verdict)

Matching is by normalized movie title. Output: public/data/movies.json
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
DATA_DIR = REPO / "public" / "data"


def normalize_title(t: str) -> str:
    """Normalize a movie title for matching."""
    t = t.lower().strip()
    # Remove common suffixes
    t = re.sub(r":\s*the\s*movie$", "", t)
    t = re.sub(r"\s*\(\d{4}\)$", "", t)  # (2026)
    t = re.sub(r"\s*\d{4}$", "", t)  # trailing year
    # Remove "review" words that leak in from headlines
    t = re.sub(r"\s*reviews?:.*$", "", t)
    t = re.sub(r"\s*review:.*$", "", t)
    # Collapse whitespace and remove non-alphanumeric
    t = re.sub(r"[^a-z0-9 ]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception as e:
        print(f"  WARN: could not load {path.name}: {e}")
        return {}


def main():
    now = datetime.now(timezone.utc)

    theaters = load_json(DATA_DIR / "now-in-theaters.json")
    boxoffice = load_json(DATA_DIR / "boxoffice.json")
    reviews_data = load_json(DATA_DIR / "movie-reviews.json")

    theater_movies = theaters.get("movies", [])
    bo_films = boxoffice.get("films", [])
    review_articles = reviews_data.get("articles", [])

    print(f"  Theaters: {len(theater_movies)}, Box office: {len(bo_films)}, Reviews: {len(review_articles)}")

    # Index box office by normalized title
    bo_by_title = {}
    for f in bo_films:
        key = normalize_title(f.get("title", ""))
        if key:
            bo_by_title[key] = f

    # Index reviews by normalized title (from first tag, fallback to headline)
    review_by_title = {}
    for a in review_articles:
        tags = a.get("tags") or []
        title = tags[0] if tags else ""
        if not title:
            # Fallback: extract from headline before colon/dash
            hl = a.get("title", "")
            m = re.match(r"^([^:—–-]+)", hl)
            title = m.group(1).strip() if m else hl
        key = normalize_title(title)
        if key and key not in review_by_title:
            # Extract rating from data_cards
            star_rating = None
            category_ratings = None
            rating_consensus = None
            for c in (a.get("data_cards") or []):
                if c.get("type") == "movie_review_ratings":
                    star_rating = c.get("star_rating")
                    category_ratings = c.get("category_ratings")
                    rating_consensus = c.get("rating_consensus")
                    break
            review_by_title[key] = {
                "review_slug": a.get("slug"),
                "review_title": a.get("title"),
                "star_rating": star_rating,
                "category_ratings": category_ratings,
                "rating_consensus": rating_consensus,
                "hero_image_url": a.get("hero_image_url"),
            }

    # Build unified movies list
    movies = []
    matched_reviews = set()
    matched_bo = set()
    unmatched = []

    # 1. Start with theater movies (now playing first)
    for m in theater_movies:
        key = normalize_title(m.get("title", ""))
        entry = {
            "title": m.get("title"),
            "slug": m.get("slug"),
            "poster_url": m.get("poster_url"),
            "language": m.get("language"),
            "genre": m.get("genre"),
            "director": m.get("director"),
            "cast": (m.get("cast") or [])[:3],
            "release_date": m.get("release_date"),
            "year": m.get("year"),
            "is_indian": m.get("is_indian", False),
            "status": m.get("status", "now_playing"),
            "ticket_url": m.get("ticket_url"),
            "trailer_url": m.get("trailer_url"),
            "rating": m.get("rating"),
            "rating_source": m.get("rating_source"),
            # Review data (if matched)
            "review_slug": None,
            "star_rating": None,
            # Box office data (if matched)
            "india_net_crore": None,
            "worldwide_gross_crore": None,
            "verdict": None,
        }

        # Match review
        if key in review_by_title:
            r = review_by_title[key]
            entry["review_slug"] = r["review_slug"]
            entry["star_rating"] = r["star_rating"]
            entry["category_ratings"] = r.get("category_ratings")
            matched_reviews.add(key)
            # Use review hero image if theater poster is missing
            if not entry["poster_url"] and r.get("hero_image_url"):
                entry["poster_url"] = r["hero_image_url"]

        # Match box office
        if key in bo_by_title:
            b = bo_by_title[key]
            entry["india_net_crore"] = b.get("india_net_crore")
            entry["worldwide_gross_crore"] = b.get("worldwide_gross_crore")
            entry["verdict"] = b.get("verdict")
            matched_bo.add(key)
            if not entry["poster_url"] and b.get("poster_url"):
                entry["poster_url"] = b["poster_url"]

        movies.append(entry)

    # 2. Add reviewed-only movies (not in theaters)
    for key, r in review_by_title.items():
        if key in matched_reviews:
            continue
        movies.append({
            "title": (r.get("review_title") or "").split(":")[0].split("—")[0].strip(),
            "slug": None,
            "poster_url": r.get("hero_image_url"),
            "language": None,
            "genre": None,
            "director": None,
            "cast": [],
            "release_date": None,
            "year": None,
            "is_indian": False,
            "status": "reviewed",
            "ticket_url": None,
            "trailer_url": None,
            "rating": None,
            "rating_source": None,
            "review_slug": r["review_slug"],
            "star_rating": r["star_rating"],
            "category_ratings": r.get("category_ratings"),
            "india_net_crore": None,
            "worldwide_gross_crore": None,
            "verdict": None,
        })
        unmatched.append(f"review-only: {key}")

    # 3. Add box-office-only films (not in theaters, no review)
    for key, b in bo_by_title.items():
        if key in matched_bo:
            continue
        # Check if already added as review-only
        if any(normalize_title(m.get("title") or "") == key for m in movies):
            # Merge box office data into existing entry
            for m in movies:
                if normalize_title(m.get("title") or "") == key:
                    m["india_net_crore"] = b.get("india_net_crore")
                    m["worldwide_gross_crore"] = b.get("worldwide_gross_crore")
                    m["verdict"] = b.get("verdict")
                    if not m.get("poster_url") and b.get("poster_url"):
                        m["poster_url"] = b["poster_url"]
                    break
            continue
        movies.append({
            "title": b.get("title"),
            "slug": None,
            "poster_url": b.get("poster_url"),
            "language": b.get("language"),
            "genre": None,
            "director": None,
            "cast": [],
            "release_date": b.get("release_date"),
            "year": None,
            "is_indian": True,
            "status": "box_office",
            "ticket_url": None,
            "trailer_url": None,
            "rating": None,
            "rating_source": None,
            "review_slug": None,
            "star_rating": None,
            "india_net_crore": b.get("india_net_crore"),
            "worldwide_gross_crore": b.get("worldwide_gross_crore"),
            "verdict": b.get("verdict"),
        })
        unmatched.append(f"boxoffice-only: {key}")

    # Sort: now-playing first (Indian first, then by release date desc), then reviewed, then box-office-only
    def sort_key(m):
        status_order = {"now_playing": 0, "coming_soon": 1, "reviewed": 2, "box_office": 3}
        s = status_order.get(m.get("status"), 4)
        indian = 0 if m.get("is_indian") else 1
        rd = m.get("release_date") or ""
        return (s, indian, rd)

    movies.sort(key=sort_key)
    # For now_playing, reverse release date (newest first) — handle separately
    now_playing = [m for m in movies if m.get("status") in ("now_playing", "coming_soon")]
    others = [m for m in movies if m.get("status") not in ("now_playing", "coming_soon")]
    now_playing.sort(key=lambda m: (
        0 if m.get("is_indian") else 1,
        m.get("release_date") or "",
    ), reverse=False)
    # Indian first, then newest release date first
    now_playing.sort(key=lambda m: (0 if m.get("is_indian") else 1, -(ord((m.get("release_date") or " ")[0]) if m.get("release_date") else 0)))
    # Simpler: stable sort by release date desc within indian/non-indian groups
    indian_np = sorted([m for m in now_playing if m.get("is_indian")],
                       key=lambda m: m.get("release_date") or "", reverse=True)
    other_np = sorted([m for m in now_playing if not m.get("is_indian")],
                      key=lambda m: m.get("release_date") or "", reverse=True)
    movies = indian_np + other_np + others

    output = {
        "generated_at": now.isoformat(),
        "week_of": theaters.get("week_of"),
        "count": len(movies),
        "movies": movies,
    }

    out_path = DATA_DIR / "movies.json"
    out_path.write_text(json.dumps(output, ensure_ascii=False, separators=(",", ":")))
    print(f"  ✓ movies.json ({len(movies)} movies)")
    print(f"  Matched reviews: {len(matched_reviews)}/{len(review_by_title)}")
    print(f"  Matched box office: {len(matched_bo)}/{len(bo_by_title)}")
    if unmatched:
        print(f"  Unmatched ({len(unmatched)}):")
        for u in unmatched[:15]:
            print(f"    - {u}")


if __name__ == "__main__":
    main()
