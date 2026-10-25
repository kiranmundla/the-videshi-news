#!/usr/bin/env python3
"""
Tests for the delayed-publish social queue:
  social_queue.py, fb-autopost.py (stage), threads-autopost.py
  (stage), reel-distribute-social.py (stage), social-publish-flush.py.

Stage modes must make ZERO connector CLI invocations — producer
modules get a subprocess.run that raises if touched (their data
fetches are mocked at the function level instead).

Run: python3 -u -m unittest test_social_queue -v
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from unittest import mock

os.environ.setdefault("SUPABASE_URL", "https://example.invalid")
os.environ.setdefault("SUPABASE_SERVICE_ROLE_KEY", "test-key")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.modules.setdefault("reel_publish", mock.MagicMock())

import social_queue as sq  # noqa: E402


def _load(mod_name, filename):
    """Producer scripts have hyphenated filenames — load by path
    (same approach as social-publish-flush.py)."""
    import importlib.util
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        filename)
    spec = importlib.util.spec_from_file_location(mod_name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[mod_name] = mod
    spec.loader.exec_module(mod)
    return mod


fb_autopost = _load("fb_autopost", "fb-autopost.py")
threads_autopost = _load("threads_autopost", "threads-autopost.py")
reel_dist = _load("reel_distribute_social", "reel-distribute-social.py")
flush = _load("social_publish_flush", "social-publish-flush.py")


def utc_now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def pacific_iso_hours_ago(hours):
    return (datetime.now(sq.PACIFIC) - timedelta(hours=hours)) \
        .isoformat(timespec="seconds")


class QueuePatchMixin:
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="sq-test-")
        self.queue_file = os.path.join(self.tmp, "queue.json")
        self._patchers = [
            mock.patch.object(sq, "QUEUE_FILE", self.queue_file),
            mock.patch.object(sq, "LOCK_FILE", self.queue_file + ".lock"),
        ]
        for p in self._patchers:
            p.start()

    def tearDown(self):
        for p in self._patchers:
            p.stop()


def make_entry(channel="facebook", kind="article_post", slug="slug-a",
               **kw):
    e = {"channel": channel, "kind": kind, "slug": slug,
         "headline": f"Headline {slug}", "text": "body text",
         "link": f"https://www.thevideshi.com/articles/{slug}",
         "media_file": None, "cover_file": None, "alt_text": None,
         "source": "test"}
    e.update(kw)
    return e


class TestQueue(QueuePatchMixin, unittest.TestCase):
    def test_add_dedup_and_order(self):
        self.assertTrue(sq.add_entry(make_entry(slug="a")))
        self.assertTrue(sq.add_entry(make_entry(slug="b")))
        self.assertTrue(sq.add_entry(make_entry(
            channel="threads", slug="a")))
        # same (channel, kind, slug) again -> dedup
        self.assertFalse(sq.add_entry(make_entry(slug="a")))
        entries = sq.load_entries()
        self.assertEqual([e["slug"] for e in entries], ["a", "b", "a"])
        self.assertTrue(all(e.get("id") for e in entries))
        self.assertTrue(all(e.get("created_at") for e in entries))

    def test_reel_dedup_keys_on_reel_id_not_slug(self):
        kw = dict(channel="facebook", kind="reel_draft", slug="same-art")
        self.assertTrue(sq.add_entry(make_entry(reel_id="vid1", **kw)))
        self.assertTrue(sq.add_entry(make_entry(reel_id="vid2", **kw)))
        self.assertFalse(sq.add_entry(make_entry(reel_id="vid1", **kw)))
        self.assertEqual(sq.queued_refs("facebook", "reel_draft"),
                         {"vid1", "vid2"})

    def test_remove_and_stale(self):
        e = make_entry(slug="old", created_at=pacific_iso_hours_ago(50))
        sq.add_entry(e)
        entries = sq.load_entries()
        self.assertTrue(sq.is_stale(entries[0]))
        self.assertTrue(sq.remove_entry(entries[0]["id"]))
        self.assertEqual(sq.load_entries(), [])
        fresh = make_entry(slug="new",
                           created_at=pacific_iso_hours_ago(1))
        sq.add_entry(fresh)
        self.assertFalse(sq.is_stale(sq.load_entries()[0]))


ARTICLE_1 = {"headline": "Big Immigration Story Breaks Today",
             "subheadline": "A major development for visa holders.",
             "slug": "big-immigration-story", "category": "immigration",
             "image_url": "https://img.example/1.jpg",
             "tags": ["H1B", "visa"]}
ARTICLE_2 = {"headline": "Markets Rally On Tech Earnings Beat",
             "subheadline": "Stocks climbed after hours.",
             "slug": "markets-rally", "category": "markets-finance",
             "image_url": None, "tags": ["stocks"]}


class TestFbStage(QueuePatchMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.fb_state = os.path.join(self.tmp, "fb-posted.json")
        self._p = [mock.patch.object(fb_autopost, "STATE_FILE",
                                     self.fb_state),
                   mock.patch.object(
                       fb_autopost.subprocess, "run",
                       side_effect=AssertionError("CLI touched"))]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def _stage(self, rows):
        with mock.patch.object(fb_autopost, "sb_get",
                               return_value=rows):
            with redirect_stdout(io.StringIO()) as buf:
                fb_autopost.stage_main()
        return buf.getvalue()

    def test_stage_picks_composes_and_writes_no_ledger(self):
        self._stage([ARTICLE_1, ARTICLE_2])
        entries = sq.load_entries()
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual(e["channel"], "facebook")
        self.assertEqual(e["kind"], "article_post")
        self.assertEqual(e["slug"], "big-immigration-story")
        self.assertEqual(e["text"], fb_autopost.build_post_text(ARTICLE_1))
        self.assertEqual(
            e["link"],
            "https://www.thevideshi.com/articles/big-immigration-story")
        self.assertIn("#TheVideshi", e["text"])
        # no fb-posted.json write at stage time
        self.assertFalse(os.path.exists(self.fb_state))

    def test_second_run_picks_next_article(self):
        self._stage([ARTICLE_1, ARTICLE_2])
        self._stage([ARTICLE_1, ARTICLE_2])
        slugs = [e["slug"] for e in sq.load_entries()]
        self.assertEqual(slugs, ["big-immigration-story", "markets-rally"])

    def test_posted_ledger_blocks_pick(self):
        with open(self.fb_state, "w") as f:
            json.dump({"posted_slugs": ["big-immigration-story"],
                       "pending_slugs": [], "abandoned_slugs": [],
                       "pending_since": {}}, f)
        out = self._stage([ARTICLE_1])
        self.assertIn("No fresh article", out)
        self.assertEqual(sq.load_entries(), [])


def t_article(slug, mins_ago, headline=None):
    ts = (datetime.now(timezone.utc) - timedelta(minutes=mins_ago)) \
        .strftime("%Y-%m-%dT%H:%M:%SZ")
    return {"headline": headline or f"Headline for {slug}",
            "subheadline": "A summary sentence for the story.",
            "slug": slug, "published_at": ts,
            "category": "news", "tags": ["india"]}


class TestThreadsStage(QueuePatchMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.fb_state = os.path.join(self.tmp, "fb-posted.json")
        self.tweet_log = os.path.join(self.tmp, "tweet-log.json")
        self.th_state = os.path.join(self.tmp, "threads-posted.json")
        with open(self.fb_state, "w") as f:
            json.dump({"posted_slugs": ["fb-slug"]}, f)
        with open(self.tweet_log, "w") as f:
            json.dump({"1": {"slug": "x-plain", "with_link": False},
                       "2": {"slug": "x-top", "with_link": True}}, f)
        with open(self.th_state, "w") as f:
            json.dump({"posted_slugs": [], "pending_slugs": [],
                       "abandoned_slugs": [], "pending_since": {},
                       "post_ids": {}}, f)
        self.rows = {
            "x-top": t_article("x-top", 10),
            "x-plain": t_article("x-plain", 20),
            "queued-fb": t_article("queued-fb", 30),
            "fb-slug": t_article("fb-slug", 40),
        }
        self._p = [
            mock.patch.object(threads_autopost, "FB_STATE", self.fb_state),
            mock.patch.object(threads_autopost, "TWEET_LOG",
                              self.tweet_log),
            mock.patch.object(threads_autopost, "STATE_FILE",
                              self.th_state),
            mock.patch.object(
                threads_autopost, "fetch_articles",
                side_effect=lambda slugs: {s: self.rows[s] for s in slugs
                                           if s in self.rows}),
            mock.patch.object(
                threads_autopost.subprocess, "run",
                side_effect=AssertionError("CLI touched")),
        ]
        for p in self._p:
            p.start()
        # an FB pick staged in the queue (not yet in fb-posted.json)
        sq.add_entry(make_entry(channel="facebook", slug="queued-fb"))

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def test_stage_link_policy_limits_and_hashtags(self):
        with redirect_stdout(io.StringIO()):
            threads_autopost.stage_main()
        entries = [e for e in sq.load_entries()
                   if e["channel"] == "threads"]
        # MAX_PER_RUN = 3, newest first: x-top, x-plain, queued-fb
        self.assertEqual([e["slug"] for e in entries],
                         ["x-top", "x-plain", "queued-fb"])
        by_slug = {e["slug"]: e for e in entries}
        self.assertIn("https://www.thevideshi.com/articles/x-top",
                      by_slug["x-top"]["text"])
        # X pick without with_link mirrors as plain text (policy v2)
        self.assertNotIn("thevideshi.com/articles",
                         by_slug["x-plain"]["text"])
        self.assertIsNone(by_slug["x-plain"]["link"])
        # staged FB pick always carries the link
        self.assertIn("https://www.thevideshi.com/articles/queued-fb",
                      by_slug["queued-fb"]["text"])
        for e in entries:
            self.assertLessEqual(len(e["text"]), 500)
            self.assertIn("#TheVideshi", e["text"])
        # threads-posted.json untouched by staging (still empty posted)
        with open(self.th_state) as f:
            self.assertEqual(json.load(f)["posted_slugs"], [])

    def test_later_runs_drain_then_stop(self):
        with redirect_stdout(io.StringIO()):
            threads_autopost.stage_main()   # stages 3 (MAX_PER_RUN)
            threads_autopost.stage_main()   # drains the 4th candidate
            threads_autopost.stage_main()   # nothing left — no dupes
        th = [e for e in sq.load_entries() if e["channel"] == "threads"]
        self.assertEqual([e["slug"] for e in th],
                         ["x-top", "x-plain", "queued-fb", "fb-slug"])


class TestReelStage(QueuePatchMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.reel_state = os.path.join(self.tmp, "reel-dist.json")
        self.mp4 = os.path.join(self.tmp, "reel.mp4")
        with open(self.mp4, "wb") as f:
            f.write(b"\0" * 2048)
        self.row = {"id": 7, "article_slug": "some-story",
                    "headline": "Reel Headline",
                    "caption": "Reel caption here #Shorts",
                    "video_path": self.mp4, "yt_video_id": "vidXYZ",
                    "status": "yt_posted", "created_at": utc_now_iso()}
        self._p = [
            mock.patch.object(reel_dist, "STATE_FILE", self.reel_state),
            mock.patch.object(reel_dist, "PIPELINE", self.tmp),
            mock.patch.object(reel_dist, "sb_get",
                              return_value=[self.row]),
            mock.patch.object(reel_dist, "yt_privacy",
                              return_value={"vidXYZ": "unlisted"}),
            mock.patch.object(
                reel_dist.subprocess, "run",
                side_effect=AssertionError("CLI touched")),
        ]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def test_stage_fb_draft_entry_ready(self):
        with redirect_stdout(io.StringIO()):
            reel_dist.main()
        entries = sq.load_entries()
        self.assertEqual(len(entries), 1)
        e = entries[0]
        self.assertEqual((e["channel"], e["kind"]),
                         ("facebook", "reel_draft"))
        self.assertEqual(e["reel_id"], "vidXYZ")
        self.assertEqual(e["media_file"], self.mp4)
        self.assertEqual(e["text"], "Reel caption here #Shorts")
        # unlisted -> no IG/Threads entries; no reel state written
        self.assertFalse(os.path.exists(self.reel_state))
        # second run does not re-stage
        with redirect_stdout(io.StringIO()):
            reel_dist.main()
        self.assertEqual(len(sq.load_entries()), 1)


class TestFlush(QueuePatchMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.fb_state = os.path.join(self.tmp, "fb-posted.json")
        self.th_state = os.path.join(self.tmp, "threads-posted.json")
        self.reel_state = os.path.join(self.tmp, "reel-dist.json")
        self.mp4 = os.path.join(self.tmp, "reel.mp4")
        with open(self.mp4, "wb") as f:
            f.write(b"\0" * 1024)
        self.order = []

        def fb_pub(entry):
            self.order.append("fb")
            return {"state": "published", "post_url": "https://fb/p1"}

        def th_pub(entry):
            self.order.append("th")
            return {"post_id": "th-1"}

        def draft(entry):
            self.order.append("draft")
            return "draft-123"
        self._p = [
            mock.patch.object(fb_autopost, "STATE_FILE", self.fb_state),
            mock.patch.object(threads_autopost, "STATE_FILE",
                              self.th_state),
            mock.patch.object(flush, "REEL_STATE_FILE", self.reel_state),
            mock.patch.object(flush, "publish_fb_article", fb_pub),
            mock.patch.object(flush, "publish_threads_article", th_pub),
            mock.patch.object(flush, "create_fb_reel_draft", draft),
        ]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def _seed_queue(self):
        sq.add_entry(make_entry(slug="art-1"))
        sq.add_entry(make_entry(channel="threads", slug="art-1"))
        sq.add_entry(make_entry(channel="facebook", kind="reel_draft",
                                slug="art-9", reel_id="vid9",
                                media_file=self.mp4))

    def test_flush_order_ledgers_and_drain(self):
        self._seed_queue()
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        self.assertEqual(self.order, ["fb", "th", "draft"])
        self.assertEqual(sq.load_entries(), [])
        with open(self.fb_state) as f:
            self.assertEqual(json.load(f)["posted_slugs"], ["art-1"])
        with open(self.th_state) as f:
            data = json.load(f)
        self.assertEqual(data["posted_slugs"], ["art-1"])
        self.assertEqual(data["post_ids"], {"art-1": "th-1"})
        with open(self.reel_state) as f:
            self.assertEqual(json.load(f)["vid9"]["fb_draft_id"],
                             "draft-123")

    def test_flush_stops_on_first_failure(self):
        self._seed_queue()
        with mock.patch.object(flush, "publish_threads_article",
                               return_value=None):
            with redirect_stdout(io.StringIO()) as buf:
                rc = flush.main()
        out = buf.getvalue()
        self.assertEqual(rc, 1)
        self.assertIn("STOPPED", out)
        remaining = sq.load_entries()
        self.assertEqual([e["channel"] for e in remaining],
                         ["threads", "facebook"])
        # FB ledger written for the one success; reel never attempted
        with open(self.fb_state) as f:
            self.assertEqual(json.load(f)["posted_slugs"], ["art-1"])
        self.assertFalse(os.path.exists(self.reel_state))

    def test_list_flags_stale(self):
        sq.add_entry(make_entry(slug="old-one",
                                created_at=pacific_iso_hours_ago(50)))
        with redirect_stdout(io.StringIO()) as buf:
            flush.print_list(sq.load_entries())
        self.assertIn("STALE", buf.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
