#!/usr/bin/env python3
"""Regression tests for the v3-select.py Step 1 fail-loud fetch guard.

Built from the 2026-11-02 incident: twice in one day (08:25 and 12:25 PT)
the selector reported "0 pending topics" and overwrote the previous good
candidate file with an EMPTY one, exiting 0, while ~9,930 topics were
pending. Root cause: sb_get() returns None on a curl/JSON failure and a
dict on a PostgREST error body, and Step 1's paging loop treated both as
end-of-pages — a failed first page was indistinguishable from "no more
pages", so the empty branch clobbered the candidate file.

The fix (fetch_pending_topics + SB_GET_LAST_ERROR in v3-select.py):
  - a None or dict page in Step 1 is a FETCH ERROR — log endpoint, page
    offset and the recorded failure evidence, exit non-zero, and never
    call write_candidates;
  - only a completed full scan that truly returns zero topics may write
    an empty candidate file (exit 0);
  - sb_get records failure evidence (curl stderr / response body) in
    SB_GET_LAST_ERROR instead of discarding it.

All Supabase access is mocked — these tests never touch the network.

Run: python3 -u test_v3_select.py
"""
import importlib.util
import os
import sys
import types
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Hermetic import of v3-select.py:
# - dummy Supabase env so the module-level credential check doesn't exit
#   (and so sb_get unit tests build URLs from dummy values);
# - a stub social_registry so the module-level IG-handle builders don't
#   do a real DB fetch at import time.
os.environ.setdefault("SUPABASE_URL", "https://example.invalid")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")

_stub_registry = types.ModuleType("social_registry")
_stub_registry.load_registry = lambda: {}
_stub_registry.get_handle_name_map = lambda platform="instagram": {}
sys.modules["social_registry"] = _stub_registry

_spec = importlib.util.spec_from_file_location(
    "v3_select", os.path.join(HERE, "v3-select.py"))
S = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(S)

FAILURES = []


def check(name, cond, detail=""):
    print(("  PASS " if cond else "  FAIL ") + name +
          (f" — {detail}" if detail and not cond else ""))
    if not cond:
        FAILURES.append(name)


CUTOFF = "2026-10-30T00:00:00Z"
COOLDOWN = "2026-11-02T00:00:00Z"


def make_topics(n, start=0):
    return [{"id": f"t{start + i}", "canonical_title": f"Topic {start + i}",
             "signal_count": 1, "status": "pending",
             "created_at": CUTOFF, "last_signal_at": CUTOFF}
            for i in range(n)]


def run_fetch(fake_sb_get):
    """Call fetch_pending_topics with a mocked sb_get.
    Returns (topics_or_None, exit_code_or_None)."""
    with mock.patch.object(S, "sb_get", fake_sb_get):
        try:
            return S.fetch_pending_topics(CUTOFF, COOLDOWN), None
        except SystemExit as e:
            return None, e.code


print("── fetch_pending_topics: fetch errors are loud ──")

# (a) First page None (curl/JSON failure) → non-zero exit.
topics, code = run_fetch(lambda *a, **k: None)
check("(a) first page None exits non-zero", code not in (None, 0),
      f"code={code}")
check("(a) first page None returns no topics", topics is None)

# (b) First page PostgREST error dict → non-zero exit.
err_body = {"code": "57014", "message": "canceling statement due to statement timeout",
            "details": None, "hint": None}
topics, code = run_fetch(lambda *a, **k: err_body)
check("(b) first page error dict exits non-zero", code not in (None, 0),
      f"code={code}")
check("(b) first page error dict returns no topics", topics is None)

# A failure on a LATER page is also an error — a partial scan must not
# pass as a completed one.
pages = iter([make_topics(1000), None])
topics, code = run_fetch(lambda *a, **k: next(pages))
check("second page None exits non-zero (no partial scan)",
      code not in (None, 0), f"code={code}")

print("── fetch_pending_topics: genuine scans unchanged ──")

# (c) Genuine empty: completed scan, zero topics → returns [], no exit.
topics, code = run_fetch(lambda *a, **k: [])
check("(c) genuine empty scan returns []", topics == [] and code is None,
      f"topics={topics} code={code}")

# (d) Normal multi-page fetch → all topics, correct page offsets.
seen_ranges = []
_multi = [make_topics(1000), make_topics(3, start=1000)]


def fake_multi(endpoint, params=None, range_header=None):
    seen_ranges.append(range_header)
    return _multi[len(seen_ranges) - 1]


topics, code = run_fetch(fake_multi)
check("(d) multi-page fetch returns all 1003 topics",
      topics is not None and len(topics) == 1003 and code is None,
      f"len={len(topics) if topics else topics} code={code}")
check("(d) multi-page fetch requested offsets 0 and 1000",
      seen_ranges == ["0-999", "1000-1999"], f"ranges={seen_ranges}")

# Single short page → exactly one request, topics returned as before.
seen_ranges = []


def fake_single(endpoint, params=None, range_header=None):
    seen_ranges.append(range_header)
    return make_topics(7)


topics, code = run_fetch(fake_single)
check("single short page returns its 7 topics in one request",
      topics is not None and len(topics) == 7 and seen_ranges == ["0-999"],
      f"len={len(topics) if topics else topics} ranges={seen_ranges}")

print("── main(): error path never touches the candidate file ──")


def run_main(fake_sb_get):
    """Run main() with sb_get / acquire_lock / write_candidates mocked.
    Returns (exit_code_or_None, list_of_write_candidates_calls)."""
    writes = []
    with mock.patch.object(S, "sb_get", fake_sb_get), \
            mock.patch.object(S, "acquire_lock", lambda: object()), \
            mock.patch.object(S, "write_candidates", writes.append):
        try:
            S.main()
            return None, writes
        except SystemExit as e:
            return e.code, writes


# (a-main) Fetch failure → non-zero exit AND candidate file untouched.
code, writes = run_main(lambda *a, **k: None)
check("(a) main exits non-zero on fetch failure", code not in (None, 0),
      f"code={code}")
check("(a) main does NOT call write_candidates on fetch failure",
      writes == [], f"writes={writes}")

# (b-main) Error dict → same.
code, writes = run_main(lambda *a, **k: err_body)
check("(b) main exits non-zero on error dict", code not in (None, 0),
      f"code={code}")
check("(b) main does NOT call write_candidates on error dict",
      writes == [], f"writes={writes}")

# (c-main) Genuine empty scan → empty candidate file written, clean return.
code, writes = run_main(lambda *a, **k: [])
check("(c) main returns cleanly on genuine empty scan", code is None,
      f"code={code}")
check("(c) main writes exactly one empty candidate file",
      len(writes) == 1 and writes[0].get("candidates") == [],
      f"writes={writes}")

print("── sb_get: failure evidence is captured ──")


def fake_run_factory(returncode=0, stdout="", stderr=""):
    def fake_run(cmd, **kwargs):
        return types.SimpleNamespace(
            returncode=returncode, stdout=stdout, stderr=stderr)
    return fake_run


# curl failure → None + evidence with kind/stderr.
with mock.patch.object(S.subprocess, "run",
                       fake_run_factory(28, "", "curl: (28) Operation timed out")):
    result = S.sb_get("p2_topics")
check("sb_get returns None on curl failure", result is None)
err = S.SB_GET_LAST_ERROR or {}
check("sb_get records curl evidence (kind + stderr)",
      err.get("kind") == "curl" and "Operation timed out" in err.get("detail", ""),
      f"err={err}")
check("sb_get evidence names the endpoint",
      err.get("endpoint") == "p2_topics", f"err={err}")

# PostgREST error body (curl exits 0) → dict returned + evidence recorded.
import json as _json
with mock.patch.object(S.subprocess, "run",
                       fake_run_factory(0, _json.dumps(err_body), "")):
    result = S.sb_get("p2_topics")
check("sb_get returns the error dict body", result == err_body)
err = S.SB_GET_LAST_ERROR or {}
check("sb_get records PostgREST error evidence",
      err.get("kind") == "postgrest_error" and "57014" in err.get("detail", ""),
      f"err={err}")

# Unparseable body → None + evidence.
with mock.patch.object(S.subprocess, "run",
                       fake_run_factory(0, "<html>proxy error</html>", "")):
    result = S.sb_get("p2_topics")
err = S.SB_GET_LAST_ERROR or {}
check("sb_get returns None + records evidence on unparseable body",
      result is None and err.get("kind") == "bad_json", f"err={err}")

# Success → list returned, evidence cleared.
with mock.patch.object(S.subprocess, "run",
                       fake_run_factory(0, _json.dumps([{"id": "t1"}]), "")):
    result = S.sb_get("p2_topics")
check("sb_get success returns rows and clears evidence",
      result == [{"id": "t1"}] and S.SB_GET_LAST_ERROR is None,
      f"result={result} err={S.SB_GET_LAST_ERROR}")

print()
if FAILURES:
    print(f"✗ {len(FAILURES)} FAILURE(S): {FAILURES}")
    sys.exit(1)
print("✓ All v3-select fetch-guard tests passed")
