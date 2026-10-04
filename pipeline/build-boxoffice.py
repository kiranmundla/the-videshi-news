#!/usr/bin/env python3
"""Build public/data/boxoffice.json from researched figures.

Usage: python3 build-boxoffice.py --figures figures.json
  figures.json: list of {title, language, release_date, india_net_crore,
    worldwide_gross_crore, budget_crore, verdict, as_of, sources:[{name,url}]}

Posters are matched from public/data/now-in-theaters.json by title.
Verdict is auto-derived from budget when not supplied:
  >=3x budget -> Blockbuster (or All-Time Blockbuster if >=5x)
  2-3x -> Super Hit, 1.5-2x -> Hit, 1-1.5x -> Average, <1x -> Flop.
"""
import json, os, sys, re
from datetime import datetime, timezone

REPO = os.path.expanduser("~/workspace/the-videshi-news")
OUT = os.path.join(REPO, "public/data/boxoffice.json")


def norm(t):
    return re.sub(r"[^a-z0-9]", "", (t or "").lower())


def derive_verdict(worldwide, budget):
    if not worldwide or not budget or budget <= 0:
        return None
    r = worldwide / budget
    if r >= 5:
        return "All-Time Blockbuster"
    if r >= 3:
        return "Blockbuster"
    if r >= 2:
        return "Super Hit"
    if r >= 1.5:
        return "Hit"
    if r >= 1:
        return "Average"
    return "Flop"


def main():
    figs_path = sys.argv[sys.argv.index("--figures") + 1]
    figs = json.load(open(figs_path))
    try:
        theaters = json.load(open(os.path.join(REPO, "public/data/now-in-theaters.json")))
        posters = {norm(m.get("title")): m.get("poster_url")
                   for m in (theaters.get("movies", []) if isinstance(theaters, dict) else theaters)}
        week_of = theaters.get("week_of") if isinstance(theaters, dict) else None
    except Exception:
        posters, week_of = {}, None

    films = []
    for f in figs:
        # Only derive when the researcher didn't make a verdict call at all.
        # An explicit null means "trades haven't called it — don't invent one."
        if "verdict" in f:
            verdict = f["verdict"]
        else:
            verdict = derive_verdict(f.get("worldwide_gross_crore"), f.get("budget_crore"))
        films.append({
            "title": f["title"],
            "language": f.get("language", ""),
            "release_date": f.get("release_date", ""),
            "india_net_crore": f.get("india_net_crore"),
            "worldwide_gross_crore": f.get("worldwide_gross_crore"),
            "budget_crore": f.get("budget_crore"),
            "verdict": verdict,
            "poster_url": posters.get(norm(f["title"])),
            "sources": f.get("sources", []),
        })
    # Sort by worldwide gross desc (unknowns last)
    films.sort(key=lambda x: (x["worldwide_gross_crore"] is None, -(x["worldwide_gross_crore"] or 0)))

    as_of = max((f.get("as_of", "") for f in figs if f.get("as_of")), default="")
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "week_of": week_of,
        "as_of": as_of,
        "films": films,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(out, open(OUT, "w"), ensure_ascii=False, indent=1)
    print(f"Wrote {OUT} with {len(films)} films (as of {as_of})")


if __name__ == "__main__":
    main()
