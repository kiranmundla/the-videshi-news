#!/usr/bin/env python3
"""Tests for the entity registry + resolution service (image
rebuild Rungs 1–2, design.md §2).

A. Registry integrity — 189 seeded entities, trap corrections.
B. Blocklist — corpus wrong-files rejected in every surface form.
C. Registry adjudication — same-name pairs split by context,
   OFFLINE (registry only, no network).
D. Live-adjudication fixtures — sitelink primacy over label-exact
   and context override, fed canned hit sets (offline).
E. Depicts license filter — NC/ND rejected, fixture payload.
F. LIVE tests (network) — run only with --live or VIDESHII_LIVE=1;
   they hit the real Wikidata/Commons APIs.

Run: python3 -u test_entity_resolve.py [--live]
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import entity_resolve as er

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


LIVE = "--live" in sys.argv or os.environ.get("VIDESHII_LIVE") == "1"

# ── A. registry integrity ────────────────────────────────────────
print("A. registry integrity")
reg = er.load_registry()
ents = reg["entities"]
by_name = {}
for e in ents:
    by_name.setdefault(e["name"], e)
check("registry has >= 189 entities", len(ents) >= 189, f"got {len(ents)}")
check("169+ entities carry a QID",
      sum(1 for e in ents if e.get("wikidata_qid")) >= 169)
check("Infosys corrected to Q26989 (not the French wholesaler)",
      by_name["Infosys"]["wikidata_qid"] == "Q26989")
check("Infosys confusable is Q134655575",
      any(c["qid_or_note"] == "Q134655575"
          for c in by_name["Infosys"]["confusables"]))
check("Infosys P18 is the campus photo",
      by_name["Infosys"]["p18_file"] == "Infosys (4911287704).jpg")
check("Supreme Court defaults to India's court Q213380",
      by_name["Supreme Court"]["wikidata_qid"] == "Q213380")
check("Supreme Court confusable is the generic concept Q190752",
      any(c["qid_or_note"] == "Q190752"
          for c in by_name["Supreme Court"]["confusables"]))
check("Bhavina Patel corrected to the athlete Q15093215",
      by_name["Bhavina Patel"]["wikidata_qid"] == "Q15093215")
check("Bhavina Patel confusable is the researcher Q102067867",
      any(c["qid_or_note"] == "Q102067867"
          for c in by_name["Bhavina Patel"]["confusables"]))
check("Jamboo Savari has NO qid (procession has no item)",
      by_name["Jamboo Savari"]["wikidata_qid"] is None)
check("Jamboo Savari confusable is the 2014 film Q17058643",
      any(c["qid_or_note"] == "Q17058643"
          for c in by_name["Jamboo Savari"]["confusables"]))
check("Blackstone confusables are the MA/VA towns",
      {c["qid_or_note"] for c in by_name["Blackstone"]["confusables"]}
      == {"Q3640815", "Q1373412"})
check("Federation Square (Melbourne) Q923304 vs Nicholls Q120485616",
      by_name["Federation Square (Melbourne)"]["wikidata_qid"] == "Q923304"
      and by_name["Federation Square, Nicholls"]["wikidata_qid"] == "Q120485616")
check("Krishna Mandir Bur Dubai has no qid; Patan is Q13183200",
      by_name["Krishna Mandir, Bur Dubai"]["wikidata_qid"] is None
      and by_name["Krishna Mandir, Patan"]["wikidata_qid"] == "Q13183200")
check("Vijay Kumar (chef) has no qid; IPS officer is Q6324218",
      by_name["Vijay Kumar (chef)"]["wikidata_qid"] is None
      and by_name["K. Vijay Kumar"]["wikidata_qid"] == "Q6324218")
check("every entry has the full schema",
      all(all(k in e for k in ("name", "aliases", "type", "wikidata_qid",
                               "p18_file", "p18_quality", "official_domain",
                               "confusables", "blocked_files", "notes"))
          for e in ents))

# ── B. blocklist ─────────────────────────────────────────────────
print("B. corpus blocklist")
M87 = "black hole - messier 87 crop max res.jpg"
check("Hindi blocks the Messier 87 file (File: form)",
      er.blocked_file("Hindi", "File:Black hole - Messier 87 crop max res.jpg"))
check("Hindi blocks the Messier 87 file (upload URL form)",
      er.blocked_file("Hindi",
                      "https://upload.wikimedia.org/wikipedia/commons/1/12/"
                      "Black_hole_-_Messier_87_crop_max_res.jpg"))
check("Hindi blocks the Messier 87 file (thumb URL form)",
      er.blocked_file("Hindi",
                      "https://upload.wikimedia.org/wikipedia/commons/thumb/"
                      "1/12/Black_hole_-_Messier_87_crop_max_res.jpg/"
                      "1024px-Black_hole_-_Messier_87_crop_max_res.jpg"))
check("Hindi does not block an unrelated file",
      not er.blocked_file("Hindi", "File:Hindi language map.png"))
check("Shadab Khan (cricketer) blocks the actor's photo-shoot file",
      er.blocked_file("Shadab Khan (cricketer)",
                      "File:Shadab Khan at photo shoot.jpg"))
check("Shadab Khan (actor) does NOT block his own file",
      not er.blocked_file("Shadab Khan (actor)",
                          "File:Shadab Khan at photo shoot.jpg"))
check("Federation Square (Melbourne) blocks the Nicholls file",
      er.blocked_file("Federation Square (Melbourne)",
                      "File:Federation Square, Nicholls 14.jpg"))
check("Ajay Kumar Srivastava blocks the Yogi felicitation file",
      er.blocked_file("Ajay Kumar Srivastava",
                      "File:Ajay_Kumar_Srivastava_and_hon._Yogi_Adityanath.jpg"))
check("file_key parity with image_ledger on Wikimedia forms",
      er.file_key("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ab/Foo_Bar.jpg/320px-Foo_Bar.jpg")
      == "foo bar.jpg")
try:
    import image_ledger as _il
    _forms = ["File:Foo Bar.jpg",
              "https://upload.wikimedia.org/wikipedia/commons/1/12/Black_hole_-_Messier_87_crop_max_res.jpg"]
    check("file_key matches image_ledger.file_key_for",
          all(er.file_key(f) == _il.file_key_for(f) for f in _forms))
except Exception as ex:  # pragma: no cover
    print(f"  SKIP file_key parity vs image_ledger ({ex})")

# ── C. registry adjudication (offline) ───────────────────────────
print("C. registry adjudication by context")
r = er.resolve("Mandeep Singh",
               "Mandeep Singh scored a drag-flick goal for India at the "
               "Asian Champions Trophy hockey tournament")
check("Mandeep Singh + hockey context -> hockey player Q6747936",
      r and r["qid"] == "Q6747936", f"got {r and r['qid']}")
r = er.resolve("Mandeep Singh",
               "Mandeep Singh smashed a fifty for Punjab in the Vijay "
               "Hazare Trophy cricket match, his third of the IPL season")
check("Mandeep Singh + cricket context -> cricketer Q6747933",
      r and r["qid"] == "Q6747933", f"got {r and r['qid']}")
r = er.resolve("Infosys", "Infosys Q2 results beat estimates")
check("Infosys -> Q26989 via registry", r and r["qid"] == "Q26989"
      and r["method"] == "registry")
r = er.resolve("Supreme Court",
               "India news: the Supreme Court in Delhi ruled on the "
               "firecracker ban ahead of Diwali")
check("Supreme Court + India context -> Q213380",
      r and r["qid"] == "Q213380", f"got {r and r['qid']}")
r = er.resolve("Shahbaz Ahmed",
               "Bengal cricketer Shahbaz Ahmed took three wickets in the "
               "Ranji Trophy match")
check("Shahbaz Ahmed + cricket context -> cricketer Q56678507",
      r and r["qid"] == "Q56678507", f"got {r and r['qid']}")
r = er.resolve("Shahbaz Ahmed",
               "Pakistan hockey legend Shahbaz Ahmed at the Olympic "
               "hockey museum event")
check("Shahbaz Ahmed + hockey context -> hockey legend Q7461476",
      r and r["qid"] == "Q7461476", f"got {r and r['qid']}")
r = er.resolve("Federation Square",
               "Diwali celebrations at Federation Square in Melbourne, Victoria")
check("Federation Square + Melbourne context -> Q923304",
      r and r["qid"] == "Q923304", f"got {r and r['qid']}")
r = er.resolve("Vijay Kumar",
               "Chef Vijay Kumar of Semma on Tamil cooking in New York")
check("bare 'Vijay Kumar' resolves to the CHEF entry (no qid), never the IPS officer",
      r and r["name"] == "Vijay Kumar (chef)" and r["qid"] is None,
      f"got {r and (r['name'], r['qid'])}")
r = er.resolve("Krishna Mandir",
               "Diwali guide to Krishna Mandir in Bur Dubai, UAE")
check("Krishna Mandir + Dubai context -> Bur Dubai entry (no qid, not Patan)",
      r and r["name"] == "Krishna Mandir, Bur Dubai" and r["qid"] is None,
      f"got {r and (r['name'], r['qid'])}")
r = er.resolve("Abhishek Sharma",
               "Abhishek Sharma hit 113 for India in the T20 cricket match")
check("Abhishek Sharma -> cricketer Q19803999 (not the ORCID stubs)",
      r and r["qid"] == "Q19803999", f"got {r and r['qid']}")

# ── D. live-adjudication fixtures (offline) ──────────────────────
print("D. adjudication fixtures — sitelink primacy + context override")
infosys_hits = [
    {"qid": "Q134655575", "label": "Infosys", "sitelinks": 1,
     "description": "foreign company wholesaling computers in France",
     "aliases": [], "p31_labels": ["organization"]},
    {"qid": "Q26989", "label": "Infosys", "sitelinks": 44,
     "description": "Indian multinational information technology company",
     "aliases": ["Infosys Limited"], "p31_labels": ["business"]},
]
w, m, _c = er._adjudicate(infosys_hits, "Infosys shares in focus today",
                          "Infosys")
check("label-exact-first French wholesaler loses to sitelink primacy",
      w and w["qid"] == "Q26989" and m == "wikidata-sitelinks",
      f"got {w and w['qid']} via {m}")
w, m, _c = er._adjudicate(infosys_hits,
                          "Indian IT services giant Infosys posts results",
                          "Infosys")
check("Infosys resolves Q26989 with Indian-IT context too",
      w and w["qid"] == "Q26989", f"got {w and w['qid']} via {m}")
court_hits = [
    {"qid": "Q190752", "label": "supreme court", "sitelinks": 95,
     "description": "highest court in a jurisdiction",
     "aliases": [], "p31_labels": []},
    {"qid": "Q213380", "label": "Supreme Court of India", "sitelinks": 47,
     "description": "Highest court of jurisdiction in the Republic of India",
     "aliases": [], "p31_labels": ["supreme court"]},
]
w, m, _c = er._adjudicate(court_hits,
                          "The Supreme Court ruled on Delhi firecrackers; "
                          "India's top court heard the plea in New Delhi",
                          "Supreme Court")
check("generic concept (95 sitelinks) loses to India's court on India context",
      w and w["qid"] == "Q213380" and m == "wikidata-context",
      f"got {w and w['qid']} via {m}")
w, m, _c = er._adjudicate(court_hits, "A supreme court decision was issued",
                          "Supreme Court")
check("neutral context falls back to sitelink primacy (generic concept)",
      w and w["qid"] == "Q190752" and m == "wikidata-sitelinks",
      f"got {w and w['qid']} via {m}")
stub_hits = [
    {"qid": "Q100000001", "label": "Mandeep Singh", "sitelinks": 0,
     "description": "researcher ORCID 0000-0003-1986-2842",
     "aliases": [], "p31_labels": ["human"]},
    {"qid": "Q6747933", "label": "Mandeep Singh", "sitelinks": 12,
     "description": "Indian cricketer", "aliases": [], "p31_labels": ["human"]},
    {"qid": "Q6747936", "label": "Mandeep Singh", "sitelinks": 18,
     "description": "Indian field hockey player",
     "aliases": [], "p31_labels": ["human"]},
]
w, m, _c = er._adjudicate(stub_hits,
                          "Mandeep Singh scored for the Indian hockey team",
                          "Mandeep Singh")
check("ORCID stubs never win; hockey context picks the hockey player",
      w and w["qid"] == "Q6747936", f"got {w and w['qid']} via {m}")

# ── E. depicts license filter (fixture) ──────────────────────────
print("E. depicts_candidates license filter (fixture payload)")
FIXTURE = {"query": {"pages": {
    "1": {"title": "File:NC example.jpg", "imageinfo": [{
        "url": "https://upload.wikimedia.org/nc.jpg", "width": 2000,
        "height": 1000, "extmetadata": {
            "License": {"value": "cc-by-nc-4.0"},
            "LicenseShortName": {"value": "CC BY-NC 4.0"}}}]},
    "2": {"title": "File:ND example.jpg", "imageinfo": [{
        "url": "https://upload.wikimedia.org/nd.jpg", "width": 2000,
        "height": 1000, "extmetadata": {
            "License": {"value": "cc-by-nd-4.0"},
            "LicenseShortName": {"value": "CC BY-ND 4.0"}}}]},
    "3": {"title": "File:BYSA example.jpg", "imageinfo": [{
        "url": "https://upload.wikimedia.org/bysa.jpg", "width": 2400,
        "height": 1200, "extmetadata": {
            "License": {"value": "cc-by-sa-4.0"},
            "LicenseShortName": {"value": "CC BY-SA 4.0"}}}]},
    "4": {"title": "File:CC0 example.jpg", "imageinfo": [{
        "url": "https://upload.wikimedia.org/cc0.jpg", "width": 1800,
        "height": 900, "extmetadata": {
            "License": {"value": "cc0-1.0"},
            "LicenseShortName": {"value": "CC0"}}}]},
    "5": {"title": "File:Unknown license.jpg", "imageinfo": [{
        "url": "https://upload.wikimedia.org/u.jpg", "width": 1800,
        "height": 900, "extmetadata": {
            "License": {"value": ""},
            "LicenseShortName": {"value": ""}}}]},
}}}
_orig_commons = er._commons_api
er._commons_api = lambda params: FIXTURE
try:
    cands = er.depicts_candidates("Q213380", limit=10)
finally:
    er._commons_api = _orig_commons
titles = {c["title"] for c in cands}
check("NC file rejected", "File:NC example.jpg" not in titles)
check("ND file rejected", "File:ND example.jpg" not in titles)
check("unknown-license file rejected (fail closed)",
      "File:Unknown license.jpg" not in titles)
check("BY-SA file accepted", "File:BYSA example.jpg" in titles)
check("CC0 file accepted", "File:CC0 example.jpg" in titles)
check("candidates carry width/height/license",
      all(c.get("width") and c.get("height") and c.get("license")
          for c in cands))

# ── F. live tests ────────────────────────────────────────────────
print("F. live Wikidata/Commons tests" + ("" if LIVE else " — SKIPPED (pass --live)"))
if LIVE:
    r = er._resolve_live("Infosys", "Indian IT services company results")
    check("LIVE _resolve_live Infosys -> Q26989",
          r and r["qid"] == "Q26989", f"got {r and r['qid']}")
    check("LIVE Infosys P18 + width returned",
          r and r["p18_file"] == "Infosys (4911287704).jpg"
          and (r["p18_quality"] or 0) >= 3000,
          f"got {r and (r['p18_file'], r['p18_quality'])}")
    r = er._resolve_live("Supreme Court",
                         "India's Supreme Court in New Delhi hears the "
                         "firecracker ban plea")
    check("LIVE _resolve_live Supreme Court + India context -> Q213380",
          r and r["qid"] == "Q213380", f"got {r and r['qid']}")
    cands = er.depicts_candidates("Q213380", limit=5)
    check("LIVE depicts_candidates(Q213380) returns >=1 clean candidate",
          len(cands) >= 1, f"got {len(cands)}")
    check("LIVE depicts candidates are all NC/ND-free",
          all("nc" not in c["license"].lower().replace(" ", "")
              and "nd" not in c["license"].lower().replace(" ", "")
              for c in cands))
    r = er._resolve_live("Mandeep Singh",
                         "Mandeep Singh scored for the Indian hockey team")
    check("LIVE _resolve_live Mandeep Singh + hockey -> Q6747936",
          r and r["qid"] == "Q6747936", f"got {r and r['qid']}")

# ── G. cache-back poisoning guard (offline, canned live) ─────
print("G. cache-back poisoning guard (canned live resolutions)")
import tempfile
_g_tmp = tempfile.mkdtemp()
_g_reg_path = os.path.join(_g_tmp, "entity_registry.json")
with open(_g_reg_path, "w") as f:
    json.dump({"version": 1, "entities": []}, f)
_orig_reg_path = er.REGISTRY_PATH
_orig_live = er._resolve_live
er.REGISTRY_PATH = _g_reg_path
er._registry_cache = None


def _canned(name, qid, aliases=None, method="wikidata-sitelinks"):
    return {"query": None, "name": name, "aliases": aliases or [],
            "qid": qid, "p18_file": None, "p18_quality": None,
            "type": "person", "method": method,
            "confidence": "high", "confusables": [],
            "blocked_files": [], "notes": "",
            "description": "canned fixture", "sitelinks": 10}


try:
    # The verbatim poison case from corpus-replay-live.json: the
    # 9-year-old guitarist Adrian Abraham's sitelink winner was
    # the rugby player Adrian Jacobs. decide() vetoed it — but
    # the unguarded _cache_back had already written Q2825029
    # into the registry under the 'Adrian Abraham' alias, where
    # registry-method results are exempt from the veto. The
    # write itself must now refuse.
    er._resolve_live = lambda n, c="": _canned(  # noqa: E731
        "Adrian Jacobs", "Q2825029")
    r = er.resolve("Adrian Abraham",
                   "Adrian Abraham, nine, of Manchester attempts "
                   "the grade 8 guitar world record")
    written = json.load(open(_g_reg_path))
    check("poisoned winner (Adrian Abraham -> Adrian Jacobs) is "
          "NOT cached into the registry",
          r and r["qid"] == "Q2825029"
          and all(e.get("wikidata_qid") != "Q2825029"
                  for e in written["entities"])
          and not er._candidates("Adrian Abraham", written),
          f"registry now: {written['entities']}")
    check("_cache_back returns False for the vetoed namesake",
          er._cache_back("Adrian Abraham",
                         _canned("Adrian Jacobs", "Q2825029"),
                         "guitar record context") is False)
    # A legitimate new resolution IS cached, with provenance.
    # SEBI's label does not contain the query token — its alias
    # does, and bearing the queried name as an alias IS bearing
    # the name (the standard names_agree applies).
    sebi = _canned("Securities and Exchange Board of India",
                   "Q2615692", aliases=["SEBI"])
    sebi["type"] = "org"
    sebi["description"] = "Indian securities market regulator"
    er._resolve_live = lambda n, c="": dict(sebi)  # noqa: E731
    ctx = ("SEBI simplifies digital KYC for NRI onboarding; the "
           "securities regulator said markets participants must "
           "comply by March")
    r = er.resolve("SEBI", ctx)
    written = json.load(open(_g_reg_path))
    sebi_entries = [e for e in written["entities"]
                    if e.get("wikidata_qid") == "Q2615692"]
    check("legitimate resolution (SEBI -> Q2615692, alias-"
          "bearing) IS cached",
          r and r["qid"] == "Q2615692" and len(sebi_entries) == 1,
          f"registry now: {written['entities']}")
    if sebi_entries:
        e0 = sebi_entries[0]
        check("cached entry records method + context provenance",
              e0.get("resolved_method") == "wikidata-sitelinks"
              and "digital KYC" in (e0.get("resolved_context")
                                    or "")
              and "SEBI" in (e0.get("aliases") or []),
              f"entry: {e0}")
    check("_cache_back returns True for a label-agreeing winner",
          er._cache_back("Nashik",
                         _canned("Nashik", "Q200235",
                                 aliases=["Nasik"]),
                         "Nashik launches EV delivery") is True)
finally:
    er._resolve_live = _orig_live
    er.REGISTRY_PATH = _orig_reg_path
    er._registry_cache = None

print()
if FAILURES:
    print(f"{len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("ALL CHECKS PASSED" + (" (incl. live)" if LIVE else " (offline set)"))
