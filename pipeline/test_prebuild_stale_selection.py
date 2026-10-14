"""Tests for prebuild-feeds.py stale-article selection (2026-10-13 fix).

prebuild-feeds.py used to rebuild individual article JSONs only for
articles published in the last 7 days, so late edits to older articles
(reviewer hero nulls, enrichments, merges — e.g. the #418 trailer merge
into an Oct 5 article) updated Supabase but never reached the live site.
select_stale_article_ids() now also selects any published article whose
DB updated_at is newer than its JSON file's mtime, or whose JSON file
is missing entirely.

Run: python3 test_prebuild_stale_selection.py  (exit 0 = all pass)
"""
import os
import sys
import tempfile
import time
from importlib.machinery import SourceFileLoader
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
mod = SourceFileLoader(
    "prebuild_feeds", os.path.join(_HERE, "prebuild-feeds.py")
).load_module()

select = mod.select_stale_article_ids

# Fixed reference point: files "written" at T0; rows updated before/after.
T0 = 1_760_000_000  # arbitrary epoch seconds
OLDER = "2025-09-05T12:00:00+00:00"        # < T0
NEWER = "2026-10-13T01:58:03.338576+00:00"  # > T0 (the #418 edit's shape)
NEWER_Z = "2026-10-13T01:58:03Z"            # Z-suffix variant


def _write(dirpath: Path, slug: str, mtime: float = T0) -> None:
    p = dirpath / f"{slug}.json"
    p.write_text("{}")
    os.utime(p, (mtime, mtime))


def main() -> int:
    failures = 0

    def check(name: str, got, expected) -> None:
        nonlocal failures
        ok = got == expected
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {name}: expect={expected} got={got}")

    with tempfile.TemporaryDirectory() as td:
        d = Path(td)
        _write(d, "edited-after-write")     # updated NEWER -> stale
        _write(d, "untouched")              # updated OLDER -> fine
        _write(d, "no-timestamp")           # updated_at None -> fine
        _write(d, "bad-timestamp")          # updated_at garbage -> fine
        _write(d, "recent-anyway")          # in recent set -> excluded
        # "missing-file" deliberately has no JSON on disk -> stale

        stamps = [
            {"id": "a1", "slug": "edited-after-write", "updated_at": NEWER},
            {"id": "a2", "slug": "untouched", "updated_at": OLDER},
            {"id": "a3", "slug": "missing-file", "updated_at": OLDER},
            {"id": "a4", "slug": "no-timestamp", "updated_at": None},
            {"id": "a5", "slug": "bad-timestamp", "updated_at": "not-a-date"},
            {"id": "a6", "slug": "recent-anyway", "updated_at": NEWER},
            {"id": "a7", "slug": "z-suffix", "updated_at": NEWER_Z},  # file missing too
            {"id": "a8", "slug": "a8", "updated_at": NEWER},          # slug == id: invalid
            {"id": "a9", "slug": None, "updated_at": NEWER},          # no slug: invalid
            {"id": "b1", "slug": "edited-after-write", "updated_at": NEWER},  # no file issue, older mtime variant below
        ]
        # Give the z-suffix article a file written long before its update.
        _write(d, "z-suffix", mtime=T0 - 100_000)

        got = select(stamps, d, recent_ids={"a6"})
        check("stale set", sorted(got), ["a1", "a3", "a7", "b1"])

        # Boundary: updated_at exactly equal to mtime is NOT stale.
        _write(d, "boundary")
        ts = time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime(T0))
        got2 = select([{"id": "c1", "slug": "boundary", "updated_at": ts}], d, set())
        check("equal mtime not stale", got2, [])

    total = 2
    print(f"\n{total - failures}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
