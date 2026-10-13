"""Regression tests for the local-news cluster title guards in
build-local-news.py (Phase 1, 2026-10-13; Phase 2 cases added same day).

The guards exist because same-name places kept polluting the wrong
bucket: San José, Costa Rica filed as San Jose, CA news; Dublin,
Ireland as Dublin, CA; "Fishers" the occupation as Fishers, IN.
Phase 2 adds the Yonkers/Bergen split (a Bergen headline must land in
the new bucket, NOT New York), the other-Clevelands blocklist,
East St. Louis, and the Orlando-the-person blocks.

A case "matches" a cluster when the compiled title pattern hits AND
cluster_blocked() does not reject the title — exactly the builder's
own gate for both article and RSS items.

Run: python3 test_local_news_guards.py  (exit 0 = all pass)
"""
import os
import sys
from importlib.machinery import SourceFileLoader

_HERE = os.path.dirname(os.path.abspath(__file__))
mod = SourceFileLoader(
    "build_local_news", os.path.join(_HERE, "build-local-news.py")
).load_module()

CLUSTERS = {c["id"]: c for c in mod.load_clusters()}
PATTERNS = {cid: mod.compile_cluster_pattern(c) for cid, c in CLUSTERS.items()}


def matches(cluster_id: str, title: str) -> bool:
    c = CLUSTERS[cluster_id]
    return bool(PATTERNS[cluster_id].search(title)) and not mod.cluster_blocked(
        c, title
    )


# (cluster_id, title, expected_match)
CASES = [
    # ── Phase 1 regression: San Jose, CA vs San José, Costa Rica ──────
    ("san-jose-ca", "India to Open New Resident Mission in San José, Costa Rica", False),
    ("san-jose-ca", "San José, Costa Rica Welcomes India's New Envoy", False),
    ("san-jose-ca", "San Jose Approves Diwali Festival Permit", True),
    # ── Phase 1: Dublin CA vs Ireland vs Dublin OH (mirror pair) ─────
    ("dublin-ca", "United Adds Dublin Route in Europe Expansion", False),
    ("dublin-ca", "Trinity College Dublin Study Links Sleep and Dementia", False),
    ("dublin-ca", "Pippal's Brings Indian Flavors to Dublin, CA", True),
    ("dublin-ca", "New Indian Restaurant Opens in Dublin, Ohio", False),
    ("columbus-oh", "New Indian Restaurant Opens in Dublin, Ohio", True),
    ("columbus-oh", "Pippal's Brings Indian Flavors to Dublin, CA", False),
    ("columbus-oh", "Dublin, California Eatery Expands to Second Location", False),
    # ── Phase 1: Edison, NJ vs Thomas Edison ──────────────────────────
    ("edison-nj", "Musk Profile Cites Thomas Edison as Inspiration", False),
    ("edison-nj", "Edison Approves New Indian Grocery Store on Oak Tree Road", True),
    # ── Phase 1: Fishers, IN vs fishers the occupation ────────────────
    ("indianapolis-in", "What Changes for Fishers Under New Seafood Rules", False),
    ("indianapolis-in", "Deep-Sea Fishers Protest New Catch Limits", False),
    ("indianapolis-in", "Fishers Approves Diwali Celebration at Nickel Plate", True),
    ("indianapolis-in", "New Hindu Temple Planned in Fishers, Indiana", True),
    # ── Phase 1: Washington DC vs Washington state ────────────────────
    ("washington-dc", "Washington State Approves New Capital Gains Tax", False),
    ("washington-dc", "Washington, D.C. Hosts Diwali Reception at Capitol", True),
    # ── Phase 1: Portland OR vs Portland ME ───────────────────────────
    ("portland-or", "Portland, Maine Seafood Festival Draws Crowds", False),
    ("portland-or", "Portland, Oregon Temple Celebrates Navratri", True),
    # ── Phase 1: Orange County CA vs FL/NC namesakes ──────────────────
    ("orange-county-ca", "Orange County, Florida Approves New Budget", False),
    ("orange-county-ca", "Orange County Fair Returns to Costa Mesa", True),
    ("orange-county-ca", "Irvine Approves New Indian Cultural Center", True),
    # ── Phase 2: Yonkers / Bergen split out of New York ────────────────
    ("yonkers-bergen-ny-nj", "Yonkers Diwali Celebration Lights Up City Hall", True),
    ("new-york-ny", "Yonkers Diwali Celebration Lights Up City Hall", False),
    ("yonkers-bergen-ny-nj", "Paramus Council Approves Indian Cultural Center", True),
    ("new-york-ny", "Paramus Council Approves Indian Cultural Center", False),
    ("yonkers-bergen-ny-nj", "Fort Lee Restaurant Week Features Indian Chefs", True),
    ("new-york-ny", "Fort Lee Restaurant Week Features Indian Chefs", False),
    ("yonkers-bergen-ny-nj", "Hackensack Temple Announces Navratri Schedule", True),
    ("new-york-ny", "Hackensack Temple Announces Navratri Schedule", False),
    ("yonkers-bergen-ny-nj", "Bergen County Issues Diwali Proclamation", True),
    ("yonkers-bergen-ny-nj", "Paterson's Indian Community Hosts Holi Festival", True),
    ("new-york-ny", "New York City Hosts Diwali at Times Square", True),
    # ── Phase 2: Cleveland, OH vs the other Clevelands ────────────────
    ("cleveland-oh", "Cleveland, Mississippi Man Sentenced in Federal Court", False),
    ("cleveland-oh", "Cleveland County Fair Opens in North Carolina", False),
    ("cleveland-oh", "Cleveland's Solon Diwali Celebration Draws Thousands", True),
    ("cleveland-oh", "New Indian Restaurant Opens in Strongsville", True),
    ("cleveland-oh", "Avon Announces New Beauty Product Line", False),
    # ── Phase 2: St. Louis, MO vs East St. Louis, IL ──────────────────
    ("st-louis-mo", "East St. Louis Approves New City Budget", False),
    ("st-louis-mo", "St. Louis Indian Community Celebrates Diwali in Chesterfield", True),
    ("st-louis-mo", "Chesterfield Mall Hosts Indian Food Festival", True),
    # ── Phase 2: Orlando, FL vs people named Orlando ──────────────────
    ("orlando-fl", "Orlando Bloom Spotted at London Film Premiere", False),
    ("orlando-fl", "Orlando Brown Arrested Again in Las Vegas", False),
    ("orlando-fl", "Orlando's Winter Park Hosts Annual Diwali Mela", True),
    ("orlando-fl", "New Indian Grocery Opens in Kissimmee", True),
    # ── Phase 2: Milwaukee, WI ────────────────────────────────────────
    ("milwaukee-wi", "Milwaukee's Indian Community Hosts Garba Night in Brookfield", True),
    ("milwaukee-wi", "Waukesha Temple Announces Navratri Schedule", True),
    # Germantown is a member (picker/distance) but deliberately NOT a
    # title alias — it is also a Maryland and Tennessee place name.
    ("milwaukee-wi", "Germantown Families Celebrate Diwali", False),
    # Brookfield is a member but NOT a title alias: the asset manager
    # (Brookfield Corporation) is a bigger namesake than Brookfield, WI
    # — build 1 filed 3 Brookfield-the-company stories here.
    ("milwaukee-wi", "Brookfield Plans to Deploy $100 Billion in India", False),
    ("milwaukee-wi", "Vance Launches H-1B Fraud Probe at Milwaukee Event", True),
]


def main() -> int:
    failures = 0
    for cid, title, expected in CASES:
        got = matches(cid, title)
        ok = got == expected
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  [{cid}] expect={expected} got={got}  {title}")
    print(f"\n{len(CASES) - failures}/{len(CASES)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
