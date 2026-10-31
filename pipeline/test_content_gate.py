#!/usr/bin/env python3
"""Tests for the pre-publish content gate (ROOT-CAUSE PROGRAM part 2,
2026-10-30 — deterministic failure-case checks at the insert choke
point, companion to the ≥2-source gate).

A. The five checks in content_gate.py, positive + negative cases.
   Failure phrasings are modelled on the Dallas BAPS article critiqued
   in ~/workspace/research_notes/gpt-brief-baps-2026-10-30/brief.md;
   the corrected versions from that brief must PASS.
B. Choke-point proof: v3-insert-article.py with a stub `curl` —
   a content-violating article is HELD (exit 2, no POST) even with
   2 valid sources; a clean article inserts.
C. v3-batch-insert.process_article refuses a violating article
   before any network call.

Run: python3 -u test_content_gate.py   (no network, no publishing)
"""
import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import content_gate as cg

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


def kinds(article):
    """Failure-kind prefixes ('unknown-value comparison', …)."""
    return [f.split(":")[0] for f in cg.check_article(article)]


print("A1. unknown-value comparison")
card_bad = {"headline": "X", "body": "<p>Text.</p>", "data_cards": [
    {"type": "price_compare", "title": "Annakut Offering",
     "headers": ["Year", "Food offered"],
     "rows": [["2025", "2,000 pounds"], ["2026", "To be determined"]]}]}
check("price_compare 2025 figure vs TBD 2026 -> HELD",
      "unknown-value comparison" in kinds(card_bad), str(kinds(card_bad)))
stat_bad = {"headline": "X", "body": "<p>Text.</p>", "data_cards": [
    {"type": "stat_grid", "title": "Offering", "items": [
        {"label": "2026 food offering", "value": "To be determined",
         "context": "vs 2,000 pounds in 2025"}]}]}
check("stat_grid value TBD with numeric context -> HELD",
      "unknown-value comparison" in kinds(stat_bad))
body_bad = {"headline": "X", "data_cards": [], "body":
            "<p>The mandir offered 2,000 pounds of food in 2025, while "
            "the 2026 total is to be determined.</p>"}
check("body sentence: figure + year + placeholder -> HELD",
      "unknown-value comparison" in kinds(body_bad))
card_ok = {"headline": "X", "body": "<p>Text.</p>", "data_cards": [
    {"type": "price_compare", "title": "Fares",
     "headers": ["Item", "Regular", "Student"],
     "rows": [["Base fare", "$1,200", "$1,080"]]}]}
check("price_compare with all real values passes",
      "unknown-value comparison" not in kinds(card_ok))
card_tba_alone = {"headline": "X", "body": "<p>Text.</p>", "data_cards": [
    {"type": "key_dates", "title": "Dates", "items": [
        {"label": "Registration opens", "value": "To be announced"}]}]}
check("lone TBA with no compared figure passes",
      "unknown-value comparison" not in kinds(card_tba_alone))
body_tba_alone = {"headline": "X", "data_cards": [], "body":
                  "<p>Officials said the exact schedule has not been "
                  "announced.</p>"}
check("honest 'not been announced' without a comparison passes",
      "unknown-value comparison" not in kinds(body_tba_alone))

print("A2. inferred admission")
adm_bad = {"headline": "X", "data_cards": [], "body":
           "<p>The festival takes place on Sunday. Admission is free "
           "and open to all visitors.</p>"}
check("bare 'Admission is free' -> HELD",
      "inferred admission" in kinds(adm_bad), str(kinds(adm_bad)))
adm_bad2 = {"headline": "X", "data_cards": [], "body":
            "<p>Entry is free, and no registration is required.</p>"}
check("bare 'Entry is free' -> HELD",
      "inferred admission" in kinds(adm_bad2))
adm_attr = {"headline": "X", "data_cards": [], "body":
            "<p>Admission is free, according to the temple.</p>"}
check("'according to the temple' passes",
      "inferred admission" not in kinds(adm_attr))
adm_attr2 = {"headline": "X", "data_cards": [], "body":
             "<p>Organizers said entry is free for devotees.</p>"}
check("'Organizers said entry is free' passes",
      "inferred admission" not in kinds(adm_attr2))
adm_unknown = {"headline": "X", "data_cards": [], "body":
               "<p>The mandir has not announced whether admission "
               "will be free.</p>"}
check("honest unknown ('whether') passes",
      "inferred admission" not in kinds(adm_unknown))
adm_neg = {"headline": "X", "data_cards": [], "body":
           "<p>Admission is not free; tickets cost $10 at the door.</p>"}
check("negated claim passes",
      "inferred admission" not in kinds(adm_neg))

print("A3. sub-event start-time invention")
sub_bad = {"headline": "X", "data_cards": [], "body":
           "<p>The celebration runs from 3 to 8 p.m. on Tuesday.</p>"
           "<p>Fireworks begin at 8 p.m. to close the evening.</p>"}
check("event 3-8pm + 'Fireworks begin at 8 p.m.' -> HELD",
      "sub-event start-time invention" in kinds(sub_bad),
      str(kinds(sub_bad)))
sub_label = {"headline": "X", "data_cards": [], "body":
             "<p>The event runs 3–8 p.m. at the mandir grounds.</p>"
             "<p>Fireworks: 8 p.m.</p>"}
check("label form 'Fireworks: 8 p.m.' -> HELD",
      "sub-event start-time invention" in kinds(sub_label))
sub_early = {"headline": "X", "data_cards": [], "body":
             "<p>The celebration runs from 3 to 8 p.m. on Tuesday.</p>"
             "<p>Fireworks begin at 7:30 p.m. over the lake.</p>"}
check("fireworks at 7:30 (not the end time) passes",
      "sub-event start-time invention" not in kinds(sub_early))
sub_notime = {"headline": "X", "data_cards": [], "body":
              "<p>The celebration runs from 3 to 8 p.m. on Tuesday.</p>"
              "<p>The evening closes with a fireworks display.</p>"}
check("closing fireworks with no start time passes",
      "sub-event start-time invention" not in kinds(sub_notime))
sub_attr = {"headline": "X", "data_cards": [], "body":
            "<p>The celebration runs from 3 to 8 p.m. on Tuesday.</p>"
            "<p>Fireworks begin at 8 p.m., organizers announced.</p>"}
check("attributed start time passes",
      "sub-event start-time invention" not in kinds(sub_attr))
sub_norange = {"headline": "X", "data_cards": [], "body":
               "<p>Fireworks begin at 8 p.m. over the lake.</p>"}
check("no event range stated -> cannot fire (documented limit)",
      "sub-event start-time invention" not in kinds(sub_norange))

print("A4. unestablished superlative lede")
led_bad = {"headline": "X", "data_cards": [], "body":
           "<p>Dallas-Fort Worth's Diwali season peaks in November "
           "with celebrations across the metroplex.</p>"
           "<p>Details follow.</p>"}
check("'season peaks' lede -> HELD",
      "unestablished superlative in lede" in kinds(led_bad),
      str(kinds(led_bad)))
led_big = {"headline": "X", "data_cards": [], "body":
           "<p>It is the biggest Diwali celebration in Texas history, "
           "drawing crowds from across the state.</p>"}
check("'biggest … in Texas history' lede -> HELD",
      "unestablished superlative in lede" in kinds(led_big))
led_attr = {"headline": "X", "data_cards": [], "body":
            "<p>Billed as the biggest Diwali celebration in the "
            "region, the festival opens on Saturday.</p>"}
check("'Billed as the biggest…' passes",
      "unestablished superlative in lede" not in kinds(led_attr))
led_attr2 = {"headline": "X", "data_cards": [], "body":
             "<p>Organizers say it will be the largest gathering of "
             "its kind in the state.</p>"}
check("'Organizers say… largest' passes",
      "unestablished superlative in lede" not in kinds(led_attr2))
led_late = {"headline": "X", "data_cards": [], "body":
            "<p>The festival opens on Saturday at the fairgrounds.</p>"
            "<p>More events follow.</p>"
            "<p>It is the biggest ever celebration for the temple.</p>"}
check("superlative outside the lede is out of scope",
      "unestablished superlative in lede" not in kinds(led_late))

print("A5. estimate-as-fact attendance")
PRE = "<p>The mandir will host its Diwali celebration on Tuesday.</p>"
est_bad = {"headline": "X", "data_cards": [], "body":
           PRE + "<p>Around 12,000 visitors attended the celebration, "
           "enjoying the Annakut display.</p>"}
check("preview article stating turnout as fact -> HELD",
      "estimate stated as fact" in kinds(est_bad), str(kinds(est_bad)))
est_ok = {"headline": "X", "data_cards": [], "body":
          PRE + "<p>Approximately 12,000 visitors are expected "
          "throughout the event, according to NBC 5's announcement.</p>"}
check("brief's corrected lede ('expected… according to') passes",
      "estimate stated as fact" not in kinds(est_ok))
est_ok2 = {"headline": "X", "data_cards": [], "body":
           PRE + "<p>The mandir expects around 12,000 visitors this "
           "year.</p>"}
check("'expects' marker passes",
      "estimate stated as fact" not in kinds(est_ok2))
est_hist = {"headline": "X", "data_cards": [], "body":
            PRE + "<p>Last year, the celebration drew 9,000 visitors "
            "over the weekend.</p>"}
check("historical turnout ('Last year… drew 9,000') passes",
      "estimate stated as fact" not in kinds(est_hist))
est_hist2 = {"headline": "X", "data_cards": [], "body":
             PRE + "<p>In 2025, the event welcomed 9,500 devotees.</p>"}
check("'In 2025…' historical figure passes",
      "estimate stated as fact" not in kinds(est_hist2))
est_report = {"headline": "X", "data_cards": [], "body":
              "<p>The celebration took place on Sunday at the "
              "fairgrounds.</p><p>A crowd of 12,000 visitors attended "
              "the event.</p>"}
check("post-event report is out of scope (documented limit)",
      "estimate stated as fact" not in kinds(est_report))

print("A5b. false-positive regressions from the 1,612-article scan")
fp_visa = {"headline": "X", "data_cards": [], "body":
           "<p>The practical path: visa-free entry and a direct flight "
           "make the trip simple.</p>"}
check("'visa-free entry' (immigration) is not an admission claim",
      "inferred admission" not in kinds(fp_visa))
fp_duty = {"headline": "X", "data_cards": [], "body":
           "<p>Exporters gain duty-free entry to New Zealand across "
           "every tariff line.</p>"}
check("'duty-free entry' (trade) is not an admission claim",
      "inferred admission" not in kinds(fp_duty))
fp_reg = {"headline": "X", "data_cards": [], "body":
          "<p>The 2026 Unified Agenda classifies the action as a "
          "long-term action whose local effects remain unknown.</p>"}
check("regulatory 'unknown' with a year but no comparison passes",
      "unknown-value comparison" not in kinds(fp_reg))
fp_pjm = {"headline": "X", "data_cards": [], "body":
          "<p>The grid operator will hold an emergency call on "
          "Monday.</p><p>PJM serves about 65 million people across "
          "13 states.</p>"}
check("'serves 65 million people' coverage stat passes",
      "estimate stated as fact" not in kinds(fp_pjm))
fp_jobs = {"headline": "X", "data_cards": [], "body":
           "<p>The company will host its investor day next week.</p>"
           "<p>It employs 11,000 people across its campuses.</p>"}
check("'employs 11,000 people' (no participation verb) passes",
      "estimate stated as fact" not in kinds(fp_jobs))
tp_people = {"headline": "X", "data_cards": [], "body":
             "<p>The temple will host its annual festival on "
             "Sunday.</p><p>More than 12,000 people attended the "
             "festival grounds celebrations.</p>"}
check("'12,000 people attended' in a preview still HELD",
      "estimate stated as fact" in kinds(tp_people))

print("A6. full BAPS-style article: all five fire; corrected passes")
bad_full = {
    "headline": "Dallas BAPS Mandir Diwali Annakut",
    "body": ("<p>Dallas-Fort Worth's Diwali season peaks this month "
             "as BAPS prepares its celebration.</p>"
             "<p>The celebration will be held on Tuesday, November 10, "
             "from 3 to 8 p.m. Admission is free and open to all.</p>"
             "<p>Fireworks begin at 8 p.m. to close the evening.</p>"
             "<p>Around 12,000 visitors attended the celebration, "
             "enjoying the Annakut display.</p>"),
    "data_cards": [
        {"type": "price_compare", "title": "Food Offering",
         "headers": ["Year", "Offering"],
         "rows": [["2025", "2,000 pounds"], ["2026", "To be determined"]]}],
}
ks = kinds(bad_full)
for want in ["unknown-value comparison", "inferred admission",
             "sub-event start-time invention",
             "unestablished superlative in lede", "estimate stated as fact"]:
    check(f"full bad article trips {want}", want in ks, str(ks))
good_full = {
    "headline": "BAPS Dallas Diwali Celebration: Annakut, Fireworks "
                "and Visitor Details for November 10",
    "body": ("<p>BAPS Shri Swaminarayan Mandir in Irving will host its "
             "Diwali and Hindu New Year celebration on Tuesday, "
             "November 10, 2026, from 3 to 8 p.m. Approximately 12,000 "
             "visitors are expected throughout the event, according to "
             "NBC 5's announcement.</p>"
             "<p>Admission and parking arrangements have not been "
             "announced; check the official BAPS Dallas page or contact "
             "the mandir.</p>"
             "<p>The evening closes with a fireworks and light-and-"
             "sound finale; the announcement does not specify an exact "
             "start time.</p>"),
    "data_cards": [],
}
check("brief's corrected article passes all checks",
      cg.check_article(good_full) == [], str(cg.check_article(good_full)))
check("malformed input never raises",
      cg.check_article(None) == [] and cg.check_article({}) == [])

print("B. v3-insert-article.py choke point (stubbed curl)")
tmp = tempfile.mkdtemp(prefix="contentgate-")
bin_dir = os.path.join(tmp, "bin")
os.makedirs(bin_dir)
curl_log = os.path.join(tmp, "curl-calls.log")
fake_curl = os.path.join(bin_dir, "curl")
with open(fake_curl, "w") as f:
    f.write("#!/bin/sh\n"
            f"echo \"$@\" >> {curl_log}\n"
            "echo '[{\"id\": \"content-gate-test-id\"}]'\n")
os.chmod(fake_curl, os.stat(fake_curl).st_mode | stat.S_IEXEC)

TWO_SOURCES = [
    {"name": "NBC 5", "url": "https://www.nbcdfw.com/about-nbc-5/community/diwali/4098187"},
    {"name": "BAPS Dallas", "url": "https://www.baps.org/Dallas"}]


def run_inserter(article):
    path = os.path.join(tmp, "article.json")
    with open(path, "w") as f:
        json.dump(article, f)
    if os.path.exists(curl_log):
        os.remove(curl_log)
    env = dict(os.environ)
    env["PATH"] = bin_dir + ":" + env["PATH"]
    env["SUPABASE_URL"] = "https://example.supabase.co"
    env["SUPABASE_SERVICE_ROLE_KEY"] = "test-key"
    r = subprocess.run(
        [sys.executable, "-u", os.path.join(HERE, "v3-insert-article.py"),
         path],
        capture_output=True, text=True, env=env, timeout=60)
    posts = 0
    if os.path.exists(curl_log):
        with open(curl_log) as f:
            posts = sum(1 for line in f
                        if "p2_articles" in line and "POST" in line)
    return r, posts


base = {"headline": "Gate Test", "subheadline": "Sub", "slug": "gate-test",
        "category": "nri-world", "sources": TWO_SOURCES}
r, posts = run_inserter(dict(base, body=bad_full["body"],
                             data_cards=bad_full["data_cards"]))
check("violating article is HELD (exit 2) despite 2 sources",
      r.returncode == 2, f"exit={r.returncode} err={r.stderr[:300]}")
check("violating article produced NO insert POST", posts == 0)
check("hold names the content gate",
      "content gate" in r.stderr.lower(), r.stderr[:200])
r, posts = run_inserter(dict(base, body=good_full["body"], data_cards=[]))
check("clean article inserts (exit 0)", r.returncode == 0,
      f"exit={r.returncode} err={r.stderr[:300]}")
check("clean article POSTed once", posts == 1)

print("C. v3-batch-insert.process_article refuses before network")
spec = importlib.util.spec_from_file_location(
    "v3_batch_insert", os.path.join(HERE, "v3-batch-insert.py"))
mod = importlib.util.module_from_spec(spec)
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
spec.loader.exec_module(mod)
calls = []
mod.sb_post = lambda ep, data: (calls.append((ep, data)) or ({"id": "x"}, None))
art = {"headline": "Bad Content Trailer", "subheadline": "s",
       "body": bad_full["body"], "slug": "bad-content-trailer",
       "category": "entertainment", "sources": TWO_SOURCES,
       "data_cards": bad_full["data_cards"]}
check("violating process_article returns False",
      mod.process_article(art) is False)
check("no sb_post call made", calls == [], f"calls={calls}")

print()
if FAILURES:
    print(f"FAILURES: {FAILURES}")
    sys.exit(1)
print("ALL CONTENT-GATE TESTS PASSED")
