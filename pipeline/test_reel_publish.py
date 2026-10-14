#!/usr/bin/env python3
"""Tests for the Phase 2 reel publish path (reel_publish.py) and the
reconciliation classifier (reel_reconcile.py). No network: all external
effects are injected fakes. Run: python3 -u test_reel_publish.py
"""

import hashlib
import inspect
import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import reel_publish as rp
import reel_reconcile as rr

PIPELINE_DIR = Path(__file__).resolve().parent
SAMPLE = (PIPELINE_DIR / "reel-samples" / "phase1"
          / "sukanya-chakrabarti-american-physical-society-fellow-dark-matter")
NEGATIVE_VERDICT = (PIPELINE_DIR / "reel-samples" / "phase1"
                    / "negative-wrong-fact" / "output" / "verdict.json")

PASSED = 0
FAILED = 0


def check(name, fn):
    global PASSED, FAILED
    try:
        fn()
        PASSED += 1
        print(f"  PASS  {name}")
    except Exception as e:  # noqa: BLE001 - test runner
        FAILED += 1
        print(f"  FAIL  {name}: {type(e).__name__}: {e}")


def expect_refused(fn, needle=""):
    try:
        fn()
    except rp.PublishRefused as e:
        assert needle.lower() in str(e).lower(), f"{needle!r} not in refusal: {e}"
        return
    raise AssertionError("expected PublishRefused, none raised")


# ------------------------------------------------------------- fixtures

def make_reel_dir(tmp, verdict_overrides=None, slug="test-article-slug"):
    """A minimal reel dir: verdict.json + script.json + article.json + mp4."""
    tmp = Path(tmp)
    mp4 = tmp / "reel.mp4"
    mp4.write_bytes(b"\x00\x00\x00\x18ftypmp42" + b"x" * 2048)
    script = {
        "news_summary": "A test summary that the fact-check gate approved.",
        "key_entities": ["Test Entity"],
        "payoff": "",
    }
    (tmp / "script.json").write_text(json.dumps(script))
    article = {"id": "11111111-2222-3333-4444-555555555555", "slug": slug,
               "headline": "Test Headline About Dark Matter",
               "subheadline": "sub", "category": "nri-world"}
    (tmp / "article.json").write_text(json.dumps(article))
    verdict = {
        "driver": "reel_produce.py", "status": "ready", "stage": "complete",
        "article_slug": slug, "script": str(tmp / "script.json"),
        "video": str(mp4),
        "factcheck": {"verdict": "pass", "held_claims": []},
        "qa": {"score": 9.5, "passed": True, "failing_checks": []},
    }
    if verdict_overrides:
        verdict.update(verdict_overrides)
    (tmp / "verdict.json").write_text(json.dumps(verdict))
    return tmp / "verdict.json", mp4


def fake_deps(events, db_rows=None, publish_entries=None, legacy_log=None):
    def get_token():
        events.append("token")
        return "fake-token"

    def upload(token, path, body):
        events.append("upload")
        assert body["status"]["privacyStatus"] == "unlisted"
        return "VID12345678"

    def verify(token, video_id):
        events.append("verify")
        return "unlisted", "Live Title"

    def append_log(entry):
        events.append("append_log")

    def write_back(article, verdict, video_path, video_id, metadata, now_iso):
        events.append("write_back")
        return {"id": "row-1", "yt_video_id": video_id, "status": "yt_posted"}

    return {
        "get_token": get_token, "upload": upload, "verify": verify,
        "append_log": append_log, "write_back": write_back,
        "db_rows": lambda slug: db_rows or [],
        "publish_entries": lambda: publish_entries or [],
        "legacy_log": lambda: legacy_log or {},
    }


# ------------------------------------------------------------- tests

def t_privacy_constant_is_unlisted():
    assert rp.PRIVACY_STATUS == "unlisted"
    body = rp.build_upload_body({"title": "t", "description": "d",
                                 "tags": ["x"]})
    assert body["status"]["privacyStatus"] == "unlisted", body


def t_privacy_cannot_be_overridden():
    src = inspect.getsource(rp.build_upload_body)
    assert "PRIVACY_STATUS" in src, "payload must be built from the constant"
    source = Path(rp.__file__).read_text()
    assert '"public"' not in source and "'public'" not in source, \
        "the public privacy literal must not exist anywhere in the module"
    params = inspect.signature(rp.publish).parameters
    assert "privacy" not in params
    params = inspect.signature(rp.build_upload_body).parameters
    assert "privacy" not in params


def t_verdict_gate_variants():
    base = {"status": "ready",
            "factcheck": {"verdict": "pass", "held_claims": []},
            "qa": {"score": 9.0, "passed": True, "failing_checks": []},
            "video": "x.mp4", "article_slug": "s"}
    assert rp.check_verdict(base) == []
    assert rp.check_verdict({**base, "status": "held"})
    assert rp.check_verdict({**base, "factcheck": {"verdict": "fail"}})
    assert rp.check_verdict({**base, "qa": {"score": 9.0, "passed": False}})
    assert rp.check_verdict({**base, "qa": {"score": 6.9, "passed": True}})
    assert rp.check_verdict({**base, "qa": {"score": None, "passed": True}})
    assert rp.check_verdict({})


def t_real_negative_sample_refused_before_any_api_call():
    events = []
    deps = fake_deps(events)
    expect_refused(lambda: rp.publish(NEGATIVE_VERDICT, deps=deps),
                   needle="fact-check")
    assert events == [], f"no external effect may happen on refusal: {events}"


def t_crafted_held_verdict_refused():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(
            tmp, verdict_overrides={"status": "held", "stage": "frame_qa",
                                    "qa": {"score": 4.0, "passed": False,
                                           "failing_checks": ["edge"]}})
        events = []
        expect_refused(lambda: rp.publish(verdict_path, deps=fake_deps(events)),
                       needle="held")
        assert events == [], events


def t_missing_verdict_refused():
    expect_refused(lambda: rp.publish("/nonexistent/verdict.json"),
                   needle="not found")


def t_duplicate_in_db_refused():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        deps = fake_deps(events, db_rows=[{"id": "r1",
                                           "yt_video_id": "OLD12345678"}])
        expect_refused(lambda: rp.publish(verdict_path, deps=deps),
                       needle="already has yt_video_id")
        assert "upload" not in events and "token" not in events, events


def t_duplicate_in_publish_log_refused():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, mp4 = make_reel_dir(tmp)
        sha = hashlib.sha256(mp4.read_bytes()).hexdigest()
        events = []
        deps = fake_deps(events, publish_entries=[
            {"video_id": "OLD12345678", "article_slug": "other-slug",
             "video_sha256": sha}])
        expect_refused(lambda: rp.publish(verdict_path, deps=deps),
                       needle="sha256")
        assert "upload" not in events, events


def t_duplicate_in_legacy_log_refused():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        deps = fake_deps(events, legacy_log={
            "reel-x.mp4": {"video_id": "LEGACY12345",
                           "article_slug": "test-article-slug",
                           "uploaded_at": "2026-10-12T00:17:00Z"}})
        expect_refused(lambda: rp.publish(verdict_path, deps=deps),
                       needle="legacy")
        assert "upload" not in events, events


def t_happy_path_order_and_result():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        result = rp.publish(verdict_path, deps=fake_deps(events))
        assert result["video_id"] == "VID12345678"
        assert result["privacy"] == "unlisted"
        # the publish log is written BEFORE the DB write-back, so a crash
        # mid-write-back can never lead to a duplicate re-upload
        assert events.index("append_log") < events.index("write_back"), events
        assert events.index("verify") < events.index("append_log"), events


def t_public_verification_is_a_hard_failure():
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        deps = fake_deps(events)
        deps["verify"] = lambda token, vid: ("public", "T")
        try:
            rp.publish(verdict_path, deps=deps)
        except rp.PublishFailed as e:
            assert "privacy" in str(e)
            assert "append_log" not in events and "write_back" not in events
            return
        raise AssertionError("expected PublishFailed on privacy mismatch")


def t_metadata_from_real_sample():
    article = json.loads((SAMPLE / "article.json").read_text())
    script = json.loads((SAMPLE / "script.json").read_text())
    meta = rp.build_metadata(article, script)
    assert meta["title"].endswith("#Shorts #DarkMatter"), meta["title"]
    assert len(meta["title"]) <= 100, len(meta["title"])
    # the long headline must not be tail-trimmed mid-entity
    # ("…Fellow of American"); leading descriptors drop instead
    assert meta["title"] == ("Astrophysicist Sukanya Chakrabarti Elected "
                             "Fellow of American Physical Society "
                             "#Shorts #DarkMatter"), meta["title"]
    assert ("https://www.thevideshi.com/articles/"
            "sukanya-chakrabarti-american-physical-society-fellow-dark-matter"
            in meta["description"])
    assert 0 < len(meta["tags"]) <= 12, meta["tags"]
    assert "Sukanya Chakrabarti" in meta["tags"]
    body = rp.build_upload_body(meta)
    assert body["status"]["privacyStatus"] == "unlisted"


def t_reconcile_classification():
    channel = {
        "INSYNC12345": {"title": "A", "published_at": "2026-07-01", "privacy": "public"},
        "LEGACY12345": {"title": "B", "published_at": "2026-10-12", "privacy": "public"},
        "UNKNOWN1234": {"title": "C", "published_at": "2026-10-12", "privacy": "public"},
        "PHASE2PUB12": {"title": "D", "published_at": "2026-10-14", "privacy": "public"},
        "PHASE2UNL12": {"title": "E", "published_at": "2026-10-14", "privacy": "unlisted"},
    }
    db_rows = [
        {"id": "r1", "article_slug": "a", "yt_video_id": "INSYNC12345",
         "status": "ready", "yt_posted_at": "2026-07-01"},
        {"id": "r2", "article_slug": "ghost", "yt_video_id": "GHOST123456",
         "status": "ready", "yt_posted_at": "2026-07-01"},
        {"id": "r3", "article_slug": "bad", "yt_video_id": "dedup-log-xyz",
         "status": "ready", "yt_posted_at": "2026-07-01"},
        {"id": "r4", "article_slug": "pending", "yt_video_id": None,
         "status": "pending", "yt_posted_at": None},
    ]
    legacy = {"reel-b.mp4": {"video_id": "LEGACY12345", "article_slug": "b",
                             "uploaded_at": "2026-10-12"}}
    pub = [{"video_id": "PHASE2PUB12"}, {"video_id": "PHASE2UNL12"}]
    rep = rr.classify(channel, db_rows, legacy, pub)
    c = rep["counts"]
    assert c["in_sync"] == 3, c
    assert c["unknown_legacy_logged"] == 1, c
    assert c["unknown_no_record"] == 1, c
    assert c["ghost_db_rows"] == 2, c
    assert c["phase2_uploads_now_public"] == 1, c
    # public + no DB record: LEGACY + UNKNOWN + (PHASE2 is logged, excluded)
    assert c["public_without_db_record"] == 2, c
    ghosts = {g["yt_video_id"]: g for g in rep["ghost_db_rows"]}
    assert ghosts["dedup-log-xyz"]["malformed_id"] is True
    assert ghosts["GHOST123456"]["malformed_id"] is False


def t_sb_write_actually_sends_the_body():
    # Regression: the first live write-back (2026-10-14) failed because
    # sb_write never passed the payload to curl — PostgREST got an empty
    # body and answered with an error object. Pin the invocation shape.
    import os
    captured = {}
    real_curl = rp.curl
    os.environ["SUPABASE_URL"] = "https://example.supabase.co"
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "k"
    rp.curl = lambda args, input_data=None, timeout=120: \
        captured.update(args=args, input=input_data) or "[]"
    try:
        rp.sb_write("POST", "prebuilt_reels", {"a": 1}, "return=representation")
    finally:
        rp.curl = real_curl
    assert "--data-binary" in captured["args"], captured["args"]
    assert "@-" in captured["args"], captured["args"]
    assert json.loads(captured["input"]) == {"a": 1}


def t_write_back_error_object_is_a_clean_failure():
    real_curl = rp.curl
    rp.curl = lambda args, input_data=None, timeout=120: json.dumps(
        {"code": "PGRST102", "message": "empty body"})
    try:
        rp.db_write_back(None, {"a": 1})
    except rp.PublishFailed as e:
        assert "empty body" in str(e)
        return
    finally:
        rp.curl = real_curl
    raise AssertionError("expected PublishFailed on PostgREST error object")


def t_reconcile_is_read_only():
    source = Path(rr.__file__).read_text()
    for banned in ("uploadType", "videos.update", "videos.insert",
                   "sb_write", '"-X", "POST"', '"-X", "DELETE"',
                   '"-X", "PUT"', '"-X", "PATCH"'):
        assert banned not in source, f"reconcile must stay read-only: {banned}"


def main():
    tests = [
        ("privacy constant is unlisted", t_privacy_constant_is_unlisted),
        ("privacy cannot be overridden", t_privacy_cannot_be_overridden),
        ("verdict gate variants", t_verdict_gate_variants),
        ("real negative sample refused pre-API",
         t_real_negative_sample_refused_before_any_api_call),
        ("crafted held verdict refused", t_crafted_held_verdict_refused),
        ("missing verdict refused", t_missing_verdict_refused),
        ("duplicate in DB refused", t_duplicate_in_db_refused),
        ("duplicate in publish log refused", t_duplicate_in_publish_log_refused),
        ("duplicate in legacy log refused", t_duplicate_in_legacy_log_refused),
        ("happy path order + result", t_happy_path_order_and_result),
        ("public verification = hard failure",
         t_public_verification_is_a_hard_failure),
        ("metadata from real Chakrabarti sample", t_metadata_from_real_sample),
        ("reconcile classification", t_reconcile_classification),
        ("sb_write sends the body (regression)", t_sb_write_actually_sends_the_body),
        ("write-back error object = clean failure",
         t_write_back_error_object_is_a_clean_failure),
        ("reconcile is read-only", t_reconcile_is_read_only),
    ]
    for name, fn in tests:
        check(name, fn)
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
