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
    state = {}

    def get_token():
        events.append("token")
        return "fake-token"

    def upload(token, path, body):
        events.append("upload")
        state["privacy"] = body["status"]["privacyStatus"]
        assert state["privacy"] in ("public", "unlisted")
        return "VID12345678"

    def verify(token, video_id):
        events.append("verify")
        return state.get("privacy", "public"), "Live Title"

    def append_log(entry):
        events.append("append_log")
        state["log_privacy"] = entry.get("privacy")

    def write_back(article, verdict, video_path, video_id, metadata,
                   now_iso, privacy="public"):
        events.append("write_back")
        state["write_back_privacy"] = privacy
        return {"id": "row-1", "yt_video_id": video_id, "status": "yt_posted"}

    return {
        "get_token": get_token, "upload": upload, "verify": verify,
        "append_log": append_log, "write_back": write_back,
        "db_rows": lambda slug: db_rows or [],
        "publish_entries": lambda: publish_entries or [],
        "legacy_log": lambda: legacy_log or {},
    }


# ------------------------------------------------------------- tests

def t_privacy_default_is_public():
    # Kiran, 2026-10-24: gate-passed reels post PUBLIC by default.
    assert rp.DEFAULT_PRIVACY == "public"
    body = rp.build_upload_body({"title": "t", "description": "d",
                                 "tags": ["x"]})
    assert body["status"]["privacyStatus"] == "public", body
    body_u = rp.build_upload_body({"title": "t", "description": "d",
                                   "tags": ["x"]}, rp.UNLISTED_PRIVACY)
    assert body_u["status"]["privacyStatus"] == "unlisted", body_u


def t_unlisted_only_via_the_flag():
    # The ONLY way to an unlisted upload is publish's unlisted flag
    # (the CLI's --unlisted; samples/tests). There is no free-form
    # privacy parameter anywhere.
    params = inspect.signature(rp.publish).parameters
    assert "privacy" not in params and "unlisted" in params
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        result = rp.publish(verdict_path, deps=fake_deps(events),
                            unlisted=True)
        assert result["privacy"] == "unlisted", result


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
        assert result["privacy"] == "public"
        pack = Path(result["tiktok_pack"])
        assert pack.exists() and "CAPTION:" in pack.read_text(), pack
        # The pack caption carries the article URL as text (Kiran,
        # 2026-10-25: links wherever allowed and free) — and it is
        # the ONLY URL in the caption.
        caption = pack.read_text().split("CAPTION:")[1]
        assert ("Full story: https://thevideshi.com/articles/"
                "test-article-slug") in caption, caption
        assert caption.count("https://") == 1, caption
        # the publish log is written BEFORE the DB write-back, so a crash
        # mid-write-back can never lead to a duplicate re-upload
        assert events.index("append_log") < events.index("write_back"), events
        assert events.index("verify") < events.index("append_log"), events


def t_privacy_mismatch_is_a_hard_failure():
    # The live privacy read-back must equal what was requested
    # (public by default); any mismatch fails before the ledgers.
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        deps = fake_deps(events)
        deps["verify"] = lambda token, vid: ("unlisted", "T")
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
    assert body["status"]["privacyStatus"] == "public"


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


def t_superseded_records_do_not_block_republish():
    # After an owner-delete + supersede, a redo of the same story must
    # pass the duplicate check (both the DB row and the log entry carry
    # superseded markers).
    with tempfile.TemporaryDirectory() as tmp:
        verdict_path, _ = make_reel_dir(tmp)
        events = []
        deps = fake_deps(
            events,
            db_rows=[{"id": "r-old", "yt_video_id": "OLD12345678",
                      "status": "superseded"}],
            publish_entries=[{"video_id": "OLD12345678",
                              "article_slug": "test-article-slug",
                              "uploaded_at": "2026-10-14T00:00:00Z",
                              "superseded": "2026-10-14T01:00:00Z"}])
        result = rp.publish(verdict_path, deps=deps)
        assert result["video_id"] == "VID12345678", result


def t_reconcile_superseded_is_not_a_ghost():
    channel = {}
    db_rows = [
        {"id": "r9", "article_slug": "redo", "yt_video_id": "GONE1234567",
         "status": "superseded", "yt_posted_at": "2026-10-14"},
        {"id": "r10", "article_slug": "ghost", "yt_video_id": "GHOST123456",
         "status": "ready", "yt_posted_at": "2026-07-01"},
    ]
    rep = rr.classify(channel, db_rows, {}, [])
    c = rep["counts"]
    assert c["ghost_db_rows"] == 1, c
    assert c["superseded_db_rows"] == 1, c
    assert rep["superseded_rows"][0]["row_id"] == "r9"
    assert rep["superseded_rows"][0]["on_channel"] is False


def _supersede_deps(events, entries, rows, exists):
    def patch_row(row_id, payload):
        events.append(("patch", row_id, payload))
        return {"id": row_id, **payload}
    return {
        "get_token": lambda: "tok",
        "video_exists": lambda token, vid: exists,
        "publish_entries": lambda: entries,
        "save_log": lambda e: events.append(("save_log", e)),
        "db_rows": lambda vid: rows,
        "patch_row": patch_row,
    }


def t_supersede_marks_both_ledgers():
    entries = [{"video_id": "VID12345678", "article_slug": "s",
                "uploaded_at": "2026-10-14T00:00:00Z"}]
    rows = [{"id": "r9", "status": "yt_posted", "qa_notes": "gate=phase2"}]
    events = []
    out = rp.supersede_video("VID12345678", "redo with better music",
                             deps=_supersede_deps(events, entries, rows,
                                                  exists=False))
    assert out["db_rows_superseded"] == ["r9"], out
    assert out["status_fallback_marker_only"] is False, out
    assert entries[0]["superseded"], entries
    assert entries[0]["superseded_reason"] == "owner_deleted_in_studio"
    assert entries[0]["superseded_note"] == "redo with better music"
    # DB is patched BEFORE the log is saved (no half-marked ledgers)
    kinds = [e[0] for e in events]
    assert kinds.index("patch") < kinds.index("save_log"), events
    kind, row_id, payload = next(e for e in events if e[0] == "patch")
    assert row_id == "r9"
    assert payload["status"] == "superseded"
    assert "owner_deleted_in_studio" in payload["qa_notes"]
    assert payload["qa_notes"].startswith("gate=phase2"), payload


def t_supersede_status_check_falls_back_to_marker():
    # The live prebuilt_reels_status_check rejects 'superseded' (proven
    # 2026-10-14); supersede must fall back to the qa_notes marker and
    # still complete both ledgers.
    entries = [{"video_id": "VID12345678", "article_slug": "s",
                "uploaded_at": "2026-10-14T00:00:00Z"}]
    rows = [{"id": "r9", "status": "yt_posted", "qa_notes": "gate=phase2"}]
    events = []

    def patch_row(row_id, payload):
        if "status" in payload:
            raise rp.PublishFailed(
                'new row violates check constraint '
                '"prebuilt_reels_status_check"')
        events.append(("patch", row_id, payload))
        return {"id": row_id, **payload}

    deps = _supersede_deps(events, entries, rows, exists=False)
    deps["patch_row"] = patch_row
    out = rp.supersede_video("VID12345678", "redo", deps=deps)
    assert out["status_fallback_marker_only"] is True, out
    kind, row_id, payload = next(e for e in events if e[0] == "patch")
    assert "status" not in payload
    assert "superseded=" in payload["qa_notes"]
    assert rp.is_superseded_row(
        {"status": "yt_posted", "qa_notes": payload["qa_notes"]})
    assert entries[0]["superseded"], entries


def t_marker_row_counts_as_superseded_everywhere():
    row = {"id": "r7", "yt_video_id": "OLD12345678", "status": "yt_posted",
           "qa_notes": "x; superseded=2026-10-14; reason=owner_deleted"}
    assert rp.is_superseded_row(row)
    reasons = rp.find_duplicates("s", "sha", [row], [], {})
    assert reasons == [], reasons
    rep = rr.classify({}, [row], {}, [])
    assert rep["counts"]["superseded_db_rows"] == 1
    assert rep["counts"]["ghost_db_rows"] == 0


def t_supersede_refuses_live_video():
    entries = [{"video_id": "VID12345678", "article_slug": "s"}]
    events = []
    expect_refused(
        lambda: rp.supersede_video(
            "VID12345678", "x",
            deps=_supersede_deps(events, entries, [], exists=True)),
        needle="still on the channel")
    assert entries[0].get("superseded") is None
    assert events == [], events


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


ROMANCH_ARTICLE = {
    "headline": "New York Bans Horse-Drawn Carriages Under Romanch's Law, "
                "Honouring Indian Teen",
    "category": "nri-world", "tags": None,
    "slug": "romanchs-law-new-york-horse-carriage-ban-indian-teen",
}
ROMANCH_SCRIPT = {
    "hook_line": "New York Bans Horse-Drawn Carriages Under Romanch's Law",
    "news_summary": "The New York City Council voted 40 to 7 to phase out "
                    "horse-drawn carriages by June 1, 2028, naming the law "
                    "for Romanch Mahajan, 18, of Pathankot.",
    "payoff": "For the Mahajan family, one outcome is already fixed.",
    "key_entities": ["New York City Council", "Central Park",
                     "Romanch Mahajan"],
}


def _tag_line(caption):
    return caption.strip().split("\n")[-1].split()


def t_tiktok_named_law_story_gets_name_tags():
    # Regression (Kiran, 2026-10-25): the Romanch's Law pack shipped
    # generic-only tags. A story named for a law/person must surface
    # that name tag.
    tags = _tag_line(rp.build_tiktok_caption(ROMANCH_ARTICLE,
                                             ROMANCH_SCRIPT))
    assert tags[0] == "#TheVideshi", tags
    assert "#RomanchsLaw" in tags, tags
    assert "#RomanchMahajan" in tags, tags
    assert len(tags) <= rp.TIKTOK_TAG_CAP, tags


def t_hashtagify_normalization():
    assert rp._hashtagify("Romanch's Law") == "#RomanchsLaw"
    assert rp._hashtagify("Romanch’s Law") == "#RomanchsLaw"
    assert rp._hashtagify("H-1B") == "#H1B"
    assert rp._hashtagify("Romanch Mahajan") == "#RomanchMahajan"
    assert rp._hashtagify("US Department of Justice") == \
        "#USDepartmentOfJustice"
    assert rp._hashtagify("!!") is None


def t_tiktok_rule_topic_and_entity_tags():
    article = {"headline": "Infosys in Talks With DOJ Over Investigation "
                           "Into H-1B Classifications",
               "category": "immigration", "tags": None}
    script = {"news_summary": "Infosys is in discussions with the US "
                              "Department of Justice.",
              "key_entities": ["Infosys", "US Department of Justice",
                               "H-1B"]}
    tags = _tag_line(rp.build_tiktok_caption(article, script))
    assert "#H1B" in tags and "#Infosys" in tags, tags
    assert "#Immigration" in tags, tags


def t_tiktok_generics_never_displace_topics():
    # Even with brand + 2 topics + category filling the cap, the
    # generic diaspora tags must be the ones squeezed out — never a
    # topic tag.
    tags = _tag_line(rp.build_tiktok_caption(ROMANCH_ARTICLE,
                                             ROMANCH_SCRIPT))
    assert len(tags) == rp.TIKTOK_TAG_CAP, tags
    assert "#IndianAmerican" not in tags, tags
    for t in ("#RomanchsLaw", "#RomanchMahajan", "#NRI"):
        assert t in tags, tags


def t_tiktok_caption_carries_story_url():
    # Kiran, 2026-10-25: article links go wherever allowed and
    # free — the TikTok caption carries the full article URL as
    # text, on its own line immediately before the hashtags.
    cap = rp.build_tiktok_caption(ROMANCH_ARTICLE, ROMANCH_SCRIPT)
    url = ("Full story: https://thevideshi.com/articles/"
           "romanchs-law-new-york-horse-carriage-ban-indian-teen")
    assert url in cap, cap
    lines = [ln for ln in cap.split("\n") if ln.strip()]
    assert lines[-2] == url, lines
    assert lines[-1].startswith("#TheVideshi"), lines
    # A slugless article gets no story line and no crash.
    cap2 = rp.build_tiktok_caption(
        {"headline": "Some Story", "category": "news", "tags": None},
        {"news_summary": "A summary."})
    assert "Full story:" not in cap2, cap2


def t_youtube_description_carries_topic_tags():
    # The description hashtag line had the same generic-only failure
    # mode via topic_hashtag's category fallback.
    meta = rp.build_metadata(ROMANCH_ARTICLE, ROMANCH_SCRIPT)
    line = meta["description"].strip().split("\n")[-1]
    assert "#RomanchsLaw" in line and "#RomanchMahajan" in line, line
    assert line.startswith("#Shorts"), line
    meta2 = rp.build_metadata(
        {"headline": "Infosys in Talks With DOJ Over H-1B Filings",
         "category": "immigration", "tags": None},
        {"news_summary": "An H-1B investigation.",
         "key_entities": ["Infosys", "H-1B"]})
    line2 = meta2["description"].strip().split("\n")[-1]
    assert "#H1B" in line2 and "#Infosys" in line2, line2


def main():
    tests = [
        ("privacy default is public", t_privacy_default_is_public),
        ("unlisted only via the flag", t_unlisted_only_via_the_flag),
        ("verdict gate variants", t_verdict_gate_variants),
        ("real negative sample refused pre-API",
         t_real_negative_sample_refused_before_any_api_call),
        ("crafted held verdict refused", t_crafted_held_verdict_refused),
        ("missing verdict refused", t_missing_verdict_refused),
        ("duplicate in DB refused", t_duplicate_in_db_refused),
        ("duplicate in publish log refused", t_duplicate_in_publish_log_refused),
        ("duplicate in legacy log refused", t_duplicate_in_legacy_log_refused),
        ("happy path order + result", t_happy_path_order_and_result),
        ("privacy mismatch = hard failure",
         t_privacy_mismatch_is_a_hard_failure),
        ("metadata from real Chakrabarti sample", t_metadata_from_real_sample),
        ("reconcile classification", t_reconcile_classification),
        ("superseded records don't block republish",
         t_superseded_records_do_not_block_republish),
        ("reconcile: superseded is not a ghost",
         t_reconcile_superseded_is_not_a_ghost),
        ("supersede marks both ledgers", t_supersede_marks_both_ledgers),
        ("supersede status-CHECK fallback to marker",
         t_supersede_status_check_falls_back_to_marker),
        ("qa_notes marker row = superseded everywhere",
         t_marker_row_counts_as_superseded_everywhere),
        ("supersede refuses a live video", t_supersede_refuses_live_video),
        ("sb_write sends the body (regression)", t_sb_write_actually_sends_the_body),
        ("write-back error object = clean failure",
         t_write_back_error_object_is_a_clean_failure),
        ("reconcile is read-only", t_reconcile_is_read_only),
        ("tiktok: named-law story gets its name tags",
         t_tiktok_named_law_story_gets_name_tags),
        ("hashtagify normalization", t_hashtagify_normalization),
        ("tiktok: rule topic + entity tags",
         t_tiktok_rule_topic_and_entity_tags),
        ("tiktok: generics never displace topics",
         t_tiktok_generics_never_displace_topics),
        ("tiktok: caption carries the full story URL",
         t_tiktok_caption_carries_story_url),
        ("youtube description carries topic tags",
         t_youtube_description_carries_topic_tags),
    ]
    for name, fn in tests:
        check(name, fn)
    print(f"\n{PASSED} passed, {FAILED} failed")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())
