#!/usr/bin/env python3
"""Tests for the ≥2-source publish gate (Kiran, approved 2026-10-14).

A. source_gate.valid_sources counting rules (dicts, bare URL strings,
   JSON-string storage, duplicates, homepage URLs, subdomain roots).
B. Choke-point proof on the real writer path: v3-insert-article.py run
   as a subprocess with a stub `curl` on PATH —
     - 1 valid source  -> exit 2, NO Supabase POST happens (held);
     - 2 valid sources -> POST happens, article id printed.
C. v3-batch-insert.process_article (trailer-watch's insert path) refuses
   a 1-source article before any network call.

Run: python3 -u test_source_gate.py   (no network, no publishing)
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

import source_gate as sg

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name + (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


print("A. valid_sources counting rules")
two = [{"name": "Reuters", "url": "https://www.reuters.com/world/india/story-1"},
       {"name": "AP", "url": "https://apnews.com/article/abc"}]
check("2 dict sources pass", sg.count_valid(two) == 2)
check("1 dict source fails", sg.gate_failure(two[:1]) is not None)
check("0 sources fail", sg.gate_failure([]) is not None)
check("bare URL strings count", sg.count_valid(
    ["https://example.com/a", "https://other.com/b"]) == 2)
check("JSON-string storage counts", sg.count_valid(json.dumps(two)) == 2)
check("duplicate URL counts once", sg.count_valid(
    [two[0], dict(two[0])]) == 1)
check("trailing-slash variant is the same source", sg.count_valid(
    [{"name": "A", "url": "https://example.com/a"},
     {"name": "B", "url": "https://example.com/a/"}]) == 1)
check("root-domain homepage does NOT count", sg.count_valid(
    [{"name": "Reuters", "url": "https://www.reuters.com"}]) == 0)
check("root-domain homepage with slash does NOT count", sg.count_valid(
    [{"name": "Reuters", "url": "https://www.reuters.com/"}]) == 0)
check("dedicated subdomain root counts (verified IR pattern)", sg.count_valid(
    [{"name": "Apple Investor Relations", "url": "https://investor.apple.com/"}]) == 1)
check("empty/garbage entries ignored", sg.count_valid(
    [{"name": "X"}, {"url": ""}, {"name": "Y", "url": "notaurl"}, None, 42]) == 0)
check("dict with URL only in name counts (normalize fallback shape)",
      sg.count_valid([{"name": "https://example.com/story", "url": ""}]) == 1)
check("two videos from one channel are 2 sources", sg.count_valid(
    [{"name": "T-Series", "url": "https://www.youtube.com/watch?v=aaa"},
     {"name": "T-Series", "url": "https://www.youtube.com/watch?v=bbb"}]) == 2)

print("B. v3-insert-article.py choke point (stubbed curl)")
tmp = tempfile.mkdtemp(prefix="srcgate-")
bin_dir = os.path.join(tmp, "bin")
os.makedirs(bin_dir)
curl_log = os.path.join(tmp, "curl-calls.log")
fake_curl = os.path.join(bin_dir, "curl")
with open(fake_curl, "w") as f:
    f.write("#!/bin/sh\n"
            f"echo \"$@\" >> {curl_log}\n"
            "echo '[{\"id\": \"gate-test-id\"}]'\n")
os.chmod(fake_curl, os.stat(fake_curl).st_mode | stat.S_IEXEC)

BASE_ARTICLE = {
    "headline": "Gate Test Story", "subheadline": "Sub",
    "body": "<p>Body text.</p>", "slug": "gate-test-story",
    "category": "news",
}


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
        [sys.executable, "-u", os.path.join(HERE, "v3-insert-article.py"), path],
        capture_output=True, text=True, env=env, timeout=60)
    posts = 0
    if os.path.exists(curl_log):
        with open(curl_log) as f:
            posts = sum(1 for line in f if "p2_articles" in line and "POST" in line)
    return r, posts


r, posts = run_inserter(dict(BASE_ARTICLE, sources=two[:1]))
check("1-source article is HELD (exit 2)", r.returncode == 2,
      f"exit={r.returncode} out={r.stdout[:120]} err={r.stderr[:200]}")
check("1-source article produced NO insert POST", posts == 0, f"posts={posts}")
check("hold is logged loudly", "HELD" in r.stderr and "source" in r.stderr.lower())

r, posts = run_inserter(dict(BASE_ARTICLE, sources=two))
check("2-source article inserts (exit 0)", r.returncode == 0,
      f"exit={r.returncode} err={r.stderr[:200]}")
check("2-source article POSTed once", posts == 1, f"posts={posts}")
check("article id reported", "gate-test-id" in r.stdout)

r, posts = run_inserter(dict(BASE_ARTICLE, sources=[
    {"name": "Reuters", "url": "https://www.reuters.com"},
    {"name": "Blog", "url": "https://example.com/post"}]))
check("homepage + 1 real page = 1 valid -> HELD", r.returncode == 2 and posts == 0,
      f"exit={r.returncode} posts={posts}")

print("C. v3-batch-insert.process_article refuses before network")
spec = importlib.util.spec_from_file_location(
    "v3_batch_insert", os.path.join(HERE, "v3-batch-insert.py"))
mod = importlib.util.module_from_spec(spec)
os.environ.setdefault("SUPABASE_URL", "https://example.supabase.co")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
spec.loader.exec_module(mod)
calls = []
mod.sb_post = lambda ep, data: (calls.append((ep, data)) or ({"id": "x"}, None))
art = {"headline": "One Source Trailer", "subheadline": "s", "body": "<p>x</p>",
       "slug": "one-source-trailer", "category": "entertainment",
       "sources": [{"name": "T-Series", "url": "https://www.youtube.com/watch?v=only1"}]}
check("1-source process_article returns False", mod.process_article(art) is False)
check("no sb_post call made", calls == [], f"calls={calls}")
art2 = dict(art, sources=[{"name": "T-Series", "url": "https://www.youtube.com/watch?v=one"},
                          {"name": "T-Series — Official YouTube Channel",
                           "url": "https://www.youtube.com/channel/UCq-Fj5jknLsUf-MWSy4_brA"}])
check("2-source process_article inserts", mod.process_article(art2) is True)
check("sb_post called once", len(calls) == 1)

print()
if FAILURES:
    print(f"FAILURES: {FAILURES}")
    sys.exit(1)
print("ALL SOURCE-GATE TESTS PASSED")
