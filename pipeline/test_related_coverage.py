#!/usr/bin/env python3
"""Tests for related_coverage relevance enforcement (2026-10-31,
root-cause program — BAPS acceptance hole 6).

The old selection treated shared tags + same category as sufficient,
so the Dallas BAPS article's baked block carried a Singapore
nightclub crime story and a missing-Ceres-woman story (shared tag
"Indian diaspora", same category) next to one relevant Diwali link.
Baseline measured on the last 7 days of published articles: 63.8% of
1,106 baked related items fail the relevance function.

A. The BAPS fixture (real published rows, test_related_fixtures.json):
   the Diwali item qualifies, the two unrelated items do not.
B. Rule units: same category alone never qualifies; a generic shared
   tag never qualifies; same entity across categories qualifies;
   storyline / topic cluster qualifies; a place entity needs a
   corroborating non-place token; headline-formula "entities" do not
   count; token routes (>=2 strong, or 1 rare non-place).
C. find_related / append_related_block with a fake DB: only
   qualifiers are linked — 1 when only 1 qualifies, none (and no
   body patch) when none qualify.

Run: python3 -u test_related_coverage.py   (no network)
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import related_coverage as rc

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


FIX = json.load(open(os.path.join(HERE, "test_related_fixtures.json")))
BAPS = FIX["dallas-baps-mandir-diwali-annakut-fireworks-november-10"]
TIMES_SQ = FIX["times-square-diwali-countdown-2026"]
SINGAPORE = FIX["indian-woman-fined-2500-molesting-singapore-"
                "nightclub-server"]
CERES = FIX["ajit-kaur-missing-ceres-woman-found-canal-california"]

# DF over just the fixture headlines (the entity route carries the
# fixture verdicts; token thresholds stay conservative at this N).
_df = {}
for _a in FIX.values():
    for _t in rc.headline_tokens(_a["headline"]):
        _df[_t] = _df.get(_t, 0) + 1
DF, DF_N = _df, len(FIX)


def Q(a, b, **kw):
    kw.setdefault("df", DF)
    kw.setdefault("df_n", DF_N)
    return rc.qualifies(a, b, **kw)


print("A. BAPS fixture (real rows)")
ok, route = Q(BAPS, TIMES_SQ)
check("BAPS -> Times Square Diwali qualifies", ok and route == "entity",
      f"got {(ok, route)}")
check("BAPS -> Singapore nightclub does NOT qualify",
      Q(BAPS, SINGAPORE) == (False, ""), f"got {Q(BAPS, SINGAPORE)}")
check("BAPS -> missing Ceres woman does NOT qualify",
      Q(BAPS, CERES) == (False, ""), f"got {Q(BAPS, CERES)}")

print("B. rule units")


def art(headline, category="nri-world", tags=None, body=None,
        image_entities=None, topic_id=None):
    return {"headline": headline, "category": category,
            "tags": tags or [], "topic_id": topic_id,
            "image_entities": image_entities,
            "body": body if body is not None
            else f"<p>{headline}. " + headline + ".</p>"}


a1 = art("Denver Council Approves New Transit Budget for 2027",
         tags=["Denver", "transit"])
a2 = art("Seattle Bakery Chain Opens Fifth Outlet Downtown",
         tags=["Seattle", "food"])
check("same category, different subject: no qualify",
      Q(a1, a2) == (False, ""), f"got {Q(a1, a2)}")

g1 = art("Temple Hosts Annual Food Festival This Weekend",
         tags=["Indian diaspora", "festival"])
g2 = art("Consulate Worker Charged in Visa Fraud Case",
         tags=["Indian diaspora", "court"])
check("generic shared tag ('Indian diaspora') alone: no qualify",
      Q(g1, g2) == (False, ""), f"got {Q(g1, g2)}")

e1 = art("Virat Kohli Signs Record Endorsement Deal", category="sports",
         image_entities=["Virat Kohli"])
e2 = art("Virat Kohli to Headline Mumbai Charity Gala",
         category="entertainment", image_entities=["Virat Kohli"])
ok, route = Q(e1, e2)
check("same entity, different category: qualifies", ok,
      f"got {(ok, route)}")

check("storyline cluster qualifies with zero overlap",
      Q(a1, a2, same_storyline=True) == (True, "storyline"))
t1 = art("Council Tables Transit Vote After Heated Hearing",
         topic_id="topic-1")
t2 = art("Commuters Face Delays as Bus Routes Are Cut",
         topic_id="topic-1")
check("same topic_id qualifies", Q(t1, t2) == (True, "topic"),
      f"got {Q(t1, t2)}")

p1 = art("Metro Extends Airport Line Timings for Holiday Rush",
         tags=["Delhi"])
p2 = art("School Wins National Robotics Prize", tags=["Delhi"])
check("place entity alone (Delhi/Delhi, disjoint topics): no qualify",
      Q(p1, p2) == (False, ""), f"got {Q(p1, p2)}")
p3 = art("Demolition Drive Paused After Court Order", tags=["Delhi"])
p4 = art("Demolition Notices Served to 40 Homes", tags=["Delhi"])
ok, route = Q(p3, p4)
check("place entity + shared non-place token: qualifies", ok,
      f"got {(ok, route)}")

_f1h = "Earnings Beat Estimates as Revenue Rises at Tech Major"
_f2h = "Earnings Beat Estimates as Revenue Rises at Pharma Major"
f1 = art(_f1h, body=f"<p>{_f1h}.</p><p>{_f1h}.</p>")
f2 = art(_f2h, body=f"<p>{_f2h}.</p><p>{_f2h}.</p>")
# realistic DF: the shared words are corpus-common, hence not strong
fdf = {"rises": 90, "beat": 80, "major": 120}
check("headline-formula 'entity' shared: no qualify",
      rc.qualifies(f1, f2, df=fdf, df_n=782) == (False, ""),
      f"got {rc.qualifies(f1, f2, df=fdf, df_n=782)}")

h1 = art("Texas Agriculture Department Bars H-1B Employers From Its "
         "State Grants", category="immigration",
         tags=["H-1B", "Texas", "grants"])
h2 = art("H-1B Workers Taking Microsoft Buyout Face 60-Day Deadline",
         category="immigration", tags=["Microsoft", "H-1B", "USCIS"])
check("shared headline-named subject tag (H-1B): qualifies",
      rc.qualifies(h1, h2, df={"h-1b": 12}, df_n=765) == (True, "entity"),
      f"got {rc.qualifies(h1, h2, df={'h-1b': 12}, df_n=765)}")
c1 = art("Delhi School Wins National Robotics Prize", tags=["Delhi"])
c2 = art("Fire Breaks Out at Delhi Warehouse Overnight", tags=["Delhi"])
check("shared city tag named in both headlines: no qualify",
      rc.qualifies(c1, c2, df={"delhi": 30}, df_n=765) == (False, ""),
      f"got {rc.qualifies(c1, c2, df={'delhi': 30}, df_n=765)}")

tok_df = {"starlink": 2, "texas": 3, "clinics": 40}
s1 = art("SpaceX Starlink Launch Lights Up Texas Sky")
s2 = art("Starlink Terminals Reach Remote Texas Clinics")
check(">=2 shared strong tokens: qualifies",
      rc.qualifies(s1, s2, df=tok_df, df_n=200) == (True, "tokens"),
      f"got {rc.qualifies(s1, s2, df=tok_df, df_n=200)}")
s3 = art("Starlink Pricing Draws Complaints From Rural Users")
check("1 shared rare non-place token: qualifies",
      rc.qualifies(s1, s3, df=tok_df, df_n=200) == (True, "tokens-rare"),
      f"got {rc.qualifies(s1, s3, df=tok_df, df_n=200)}")
s4 = art("Clinics Report Surge in Winter Flu Visits")
check("shared token too common to be strong: no qualify",
      rc.qualifies(s2, s4, df=tok_df, df_n=200) == (False, ""),
      f"got {rc.qualifies(s2, s4, df=tok_df, df_n=200)}")
check("df=None disables the single-token route",
      rc.qualifies(s1, s3, df=None, df_n=0) == (False, ""),
      f"got {rc.qualifies(s1, s3, df=None, df_n=0)}")

print("C. find_related / append with a fake DB")

CANDS = {a["id"]: a for a in (TIMES_SQ, SINGAPORE, CERES)}
PATCHED = {}


def fake_get(path, params=()):
    P = dict(params)
    if path == "storyline_articles":
        return []
    if path != "p2_articles":
        return []
    sel = P.get("select", "")
    if sel == "headline":  # token-DF fetch
        return ([{"headline": h} for h in
                 ["Diwali Celebrations Light Up City",
                  "Markets Close Higher on Earnings",
                  "Cricket Team Announces Squad"]] * 10)
    if "id" in P and P["id"].startswith("in.("):
        ids = P["id"][4:-1].split(",")
        return [CANDS[i] for i in ids if i in CANDS]
    if "id" in P and P["id"].startswith("eq."):
        aid = P["id"][3:]
        if aid in CANDS:
            return [CANDS[aid]]
        return [BAPS] if aid == BAPS["id"] else []
    if "tags" in P:  # tags cs.{...}
        tag = P["tags"][4:-1]
        return [a for a in CANDS.values()
                if tag in (a.get("tags") or [])][:10]
    if "category" in P:
        cat = P["category"][3:]
        return [a for a in CANDS.values()
                if a.get("category") == cat][:30]
    return []


def fake_patch(path, params, data):
    PATCHED.update(data)
    return True


_orig_get, _orig_patch = rc._get, rc._patch
rc._get, rc._patch = fake_get, fake_patch
rc._DF_CACHE.update({"t": 0.0, "df": None, "n": 0})
try:
    rel = rc.find_related(BAPS["id"], BAPS["category"], BAPS["tags"],
                          article=BAPS)
    check("find_related returns only the qualifier (1 of 3)",
          [r["slug"] for r in rel] == [TIMES_SQ["slug"]],
          f"got {[r['slug'] for r in rel]}")

    rel0 = rc.find_related(BAPS["id"], BAPS["category"],
                           ["Indian diaspora"], article=BAPS)
    check("tag breadth alone still yields only qualifiers",
          all(r["slug"] == TIMES_SQ["slug"] for r in rel0),
          f"got {[r['slug'] for r in rel0]}")

    stripped = dict(BAPS)
    i = stripped["body"].find('<div class="related-coverage">')
    stripped["body"] = stripped["body"][:i]
    CANDS[BAPS["id"]] = stripped  # append fetches source via _get eq.
    n = rc.append_related_block(BAPS["id"])
    body = PATCHED.get("body", "")
    check("append links exactly 1", n == 1, f"got {n}")
    check("appended block carries the Diwali link only",
          TIMES_SQ["slug"] in body
          and SINGAPORE["slug"] not in body
          and CERES["slug"] not in body)
finally:
    rc._get, rc._patch = _orig_get, _orig_patch

PATCHED.clear()
rc._get, rc._patch = fake_get, fake_patch
rc._DF_CACHE.update({"t": 0.0, "df": None, "n": 0})
try:
    lone = art("Harbor Festival Announces Weekend Lineup",
               tags=["Indian diaspora"])
    lone["id"] = "lone-source-id"
    lone["body"] = "<p>Harbor Festival Announces Weekend Lineup.</p>"
    CANDS[lone["id"]] = lone
    # candidates reachable (same category / shared generic tag) but
    # none qualify -> no block, no patch
    n = rc.append_related_block(lone["id"])
    check("no qualifiers: append returns 0 and patches nothing",
          n == 0 and "body" not in PATCHED, f"got n={n}")
finally:
    rc._get, rc._patch = _orig_get, _orig_patch

check("render of empty selection is empty",
      rc.render_related_block([]) == "")

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED")
