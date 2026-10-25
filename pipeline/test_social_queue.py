#!/usr/bin/env python3
"""
Tests for the delayed-publish social queue:
  social_queue.py, fb-autopost.py (stage), threads-autopost.py
  (stage), reel-distribute-social.py (stage), social-publish-flush.py.

Stage modes must make ZERO connector CLI invocations — producer
modules get a subprocess.run that raises if touched (their data
fetches are mocked at the function level instead).

Card coverage (go-live 2026-10-24; card SETS same night): staging
attaches card_files / card_texts / card_track (FB renders the set,
Threads shares or generates it, IG stages only the hook card and
only when a set exists, the <600px skip leaves the set empty),
the flush publishes the whole set on FB (repeated --file) and
Threads (ordered --media-items), and x-autopost attaches the set
at post time via x_cards (all-or-nothing).

Run: python3 -u -m unittest test_social_queue -v
"""
import io
import json
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
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

    def test_stage_with_card_set_also_stages_ig_hook_only(self):
        files = []
        for n in (1, 2, 3, 4):
            p = os.path.join(self.tmp, f"card-{n}.png")
            with open(p, "wb") as f:
                f.write(b"\x89PNG")
            files.append(p)
        texts = ["Big Immigration Story Breaks Today", "Takeaway one.",
                 "Takeaway two.", "Full story at thevideshi.com"]
        with mock.patch.object(fb_autopost, "generate_card_set",
                               return_value=(files, "backdrop", texts)):
            self._stage([ARTICLE_1, ARTICLE_2])
        entries = sq.load_entries()
        self.assertEqual(len(entries), 2)
        fb_e, ig_e = entries
        # FB carries the whole ordered set; card_file is the hook
        self.assertEqual(fb_e["card_files"], files)
        self.assertEqual(fb_e["card_file"], files[0])
        self.assertEqual(fb_e["card_texts"], texts)
        self.assertEqual(fb_e["card_track"], "backdrop")
        # IG stays single-card: the hook only, IG caption carrying
        # the full article URL as text (Kiran, 2026-10-25: links
        # wherever allowed and free), and no card_files of its own
        self.assertEqual((ig_e["channel"], ig_e["kind"]),
                         ("instagram", "article_post"))
        self.assertEqual(ig_e["slug"], "big-immigration-story")
        self.assertEqual(ig_e["card_file"], files[0])
        self.assertIsNone(ig_e.get("card_files"))
        self.assertEqual(ig_e["card_track"], "backdrop")
        story = ("Full story: https://thevideshi.com/articles/"
                 "big-immigration-story")
        self.assertIn(story, ig_e["text"])
        self.assertNotIn("Full story at thevideshi.com", ig_e["text"])
        # The story line sits before the hashtag line.
        self.assertLess(ig_e["text"].index(story),
                        ig_e["text"].index("#TheVideshi"))
        self.assertIn("#TheVideshi", ig_e["text"])
        self.assertIsNone(ig_e["link"])

    def test_stage_card_set_skipped_no_ig(self):
        with mock.patch.object(fb_autopost, "generate_card_set",
                               return_value=([], "skipped", [])):
            self._stage([ARTICLE_1])
        entries = sq.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertIsNone(entries[0]["card_file"])
        self.assertIsNone(entries[0]["card_files"])
        self.assertEqual(entries[0]["card_track"], "skipped")

    def test_stage_card_set_failure_still_stages_cardless(self):
        with mock.patch.object(fb_autopost, "generate_card_set",
                               return_value=([], None, [])):
            self._stage([ARTICLE_1])
        entries = sq.load_entries()
        self.assertEqual(len(entries), 1)
        self.assertIsNone(entries[0]["card_file"])
        self.assertIsNone(entries[0]["card_files"])
        self.assertIsNone(entries[0]["card_track"])


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
        # X pick without with_link STILL mirrors with the link
        # (2026-10-25: Threads posts are free — always link; X's
        # with_link flag is not inherited)
        self.assertIn("https://www.thevideshi.com/articles/x-plain",
                      by_slug["x-plain"]["text"])
        self.assertEqual(by_slug["x-plain"]["link"],
                         "https://www.thevideshi.com/articles/x-plain")
        self.assertTrue(by_slug["x-plain"]["with_link"])
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

    def test_build_text_link_survives_tight_char_budget(self):
        # Over-long subheadline: the 500-char trim must cut the
        # subheadline, never the link or the hashtag line.
        article = {"headline": "A Moderately Long Headline About "
                               "Something Important Happening Today",
                   "subheadline": "word " * 120,
                   "slug": "tight-budget-story",
                   "category": "news", "tags": ["india"]}
        text = threads_autopost.build_text(article)
        self.assertLessEqual(len(text), 500)
        self.assertIn(
            "https://www.thevideshi.com/articles/tight-budget-story",
            text)
        self.assertIn("#TheVideshi", text)

    def test_mirror_shares_fb_card_set_and_generates_own(self):
        shared = ["/cards/x-top-1.png", "/cards/x-top-2.png",
                  "/cards/x-top-3.png"]
        shared_texts = ["Headline for x-top", "A takeaway.",
                        "Full story at thevideshi.com"]
        sq.add_entry(make_entry(channel="facebook", slug="x-top",
                                card_file=shared[0], card_files=shared,
                                card_texts=shared_texts,
                                card_track="backdrop"))
        calls = []

        def fake_gen(article):
            calls.append(article["slug"])
            return (["/cards/gen-1.png", "/cards/gen-2.png"],
                    "full-bleed", ["H", "Full story at thevideshi.com"])

        with mock.patch.object(threads_autopost, "generate_card_set",
                               side_effect=fake_gen):
            with redirect_stdout(io.StringIO()):
                threads_autopost.stage_main()
        entries = {e["slug"]: e for e in sq.load_entries()
                   if e["channel"] == "threads"}
        # FB counterpart's SET: shared files/texts, never regenerated
        self.assertEqual(entries["x-top"]["card_files"], shared)
        self.assertEqual(entries["x-top"]["card_file"], shared[0])
        self.assertEqual(entries["x-top"]["card_texts"], shared_texts)
        self.assertEqual(entries["x-top"]["card_track"], "backdrop")
        # X-only pick and the set-less staged FB pick generate their own
        self.assertEqual(entries["x-plain"]["card_files"],
                         ["/cards/gen-1.png", "/cards/gen-2.png"])
        self.assertEqual(entries["queued-fb"]["card_files"],
                         ["/cards/gen-1.png", "/cards/gen-2.png"])
        self.assertEqual(sorted(calls), ["queued-fb", "x-plain"])

    def test_mirror_inherits_fb_skip(self):
        sq.add_entry(make_entry(channel="facebook", slug="x-plain",
                                card_file=None, card_files=None,
                                card_track="skipped"))
        calls = []

        def fake_gen(article):
            calls.append(article["slug"])
            return (["/cards/gen-1.png"], "full-bleed", ["H"])

        with mock.patch.object(threads_autopost, "generate_card_set",
                               side_effect=fake_gen):
            with redirect_stdout(io.StringIO()):
                threads_autopost.stage_main()
        entries = {e["slug"]: e for e in sq.load_entries()
                   if e["channel"] == "threads"}
        self.assertIsNone(entries["x-plain"]["card_file"])
        self.assertIsNone(entries["x-plain"]["card_files"])
        self.assertEqual(entries["x-plain"]["card_track"], "skipped")
        self.assertNotIn("x-plain", calls)


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


class TestFlushCards(QueuePatchMixin, unittest.TestCase):
    """Flush with staged social cards: FB attaches the card file,
    Threads carries it as a media item, IG publishes it as a photo
    post via post-feed. The producers' publish functions and the
    CLIs are mocked at the boundary; the flush's own card dispatch
    logic runs for real."""

    def setUp(self):
        super().setUp()
        self.fb_state = os.path.join(self.tmp, "fb-posted.json")
        self.th_state = os.path.join(self.tmp, "threads-posted.json")
        self.reel_state = os.path.join(self.tmp, "reel-dist.json")
        self.card = os.path.join(self.tmp, "card.png")
        with open(self.card, "wb") as f:
            f.write(b"\x89PNG fake")
        self.calls = []

        def fb_publish(text, url, image_url=None, image_path=None):
            self.calls.append(("fb", image_path))
            return {"state": "published", "post_url": "https://fb/c1"}

        def fake_run(cmd, **kw):
            self.calls.append((cmd[0].rsplit("/", 1)[-1], cmd))
            payload = ({"post_id": "th-card"} if "threads-cli" in cmd[0]
                       else {"post_id": "ig-card"})
            return mock.Mock(stdout=json.dumps(payload), returncode=0)

        self._p = [
            mock.patch.object(fb_autopost, "STATE_FILE", self.fb_state),
            mock.patch.object(threads_autopost, "STATE_FILE",
                              self.th_state),
            mock.patch.object(flush, "REEL_STATE_FILE", self.reel_state),
            mock.patch.object(fb_autopost, "publish", fb_publish),
            mock.patch.object(flush.subprocess, "run", fake_run),
        ]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def _card_entry(self, channel, slug="card-story"):
        return make_entry(channel=channel, slug=slug,
                          card_file=self.card, card_track="backdrop",
                          image_url="https://img.example/hero.jpg")

    def test_flush_publishes_cards_all_channels(self):
        sq.add_entry(self._card_entry("facebook"))
        sq.add_entry(self._card_entry("threads"))
        sq.add_entry(self._card_entry("instagram"))
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        self.assertEqual(sq.load_entries(), [])
        self.assertEqual([c[0] for c in self.calls],
                         ["fb", "threads-cli", "instagram-cli"])
        # FB attached the card file itself (image_path), not a hero
        self.assertEqual(self.calls[0][1], self.card)
        # Threads carried the card as a media item; images take no cover
        th_cmd = self.calls[1][1]
        item = json.loads(th_cmd[th_cmd.index("--media-item") + 1])
        self.assertEqual(item["file"], self.card)
        self.assertNotIn("cover", item)
        # IG posted the card as a photo: post-feed --file, no --cover
        ig_cmd = self.calls[2][1]
        self.assertIn("post-feed", ig_cmd)
        self.assertEqual(ig_cmd[ig_cmd.index("--file") + 1], self.card)
        self.assertNotIn("--cover", ig_cmd)
        # ledgers written as today
        with open(self.fb_state) as f:
            self.assertEqual(json.load(f)["posted_slugs"], ["card-story"])
        with open(self.th_state) as f:
            self.assertEqual(json.load(f)["post_ids"],
                             {"card-story": "th-card"})

    def test_ig_article_missing_card_stops_flush(self):
        e = self._card_entry("instagram")
        e["card_file"] = os.path.join(self.tmp, "gone.png")
        sq.add_entry(e)
        with redirect_stdout(io.StringIO()) as buf:
            rc = flush.main()
        self.assertEqual(rc, 1)
        self.assertIn("STOPPED", buf.getvalue())
        self.assertEqual(len(sq.load_entries()), 1)

    def test_fb_article_missing_card_falls_back_to_hero(self):
        e = self._card_entry("facebook")
        e["card_file"] = os.path.join(self.tmp, "gone.png")
        sq.add_entry(e)
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        # publish() invoked with no image_path -> plain-hero behavior
        self.assertEqual(self.calls, [("fb", None)])

    def test_list_annotates_cards(self):
        sq.add_entry(self._card_entry("facebook", slug="with-card"))
        sq.add_entry(make_entry(slug="skipped-card", card_file=None,
                                card_track="skipped"))
        sq.add_entry(make_entry(slug="plain"))
        with redirect_stdout(io.StringIO()) as buf:
            flush.print_list(sq.load_entries())
        out = buf.getvalue()
        self.assertIn("card: backdrop", out)
        self.assertIn("card: none (<600px skip)", out)
        self.assertIn("card: none", out)


class TestFlushCardSets(QueuePatchMixin, unittest.TestCase):
    """Flush with staged card SETS: FB attaches every card via
    image_paths (repeated --file), Threads passes every card as an
    ordered --media-item with its own alt text, and --list shows
    the set size. Producer publish + CLIs mocked at the boundary."""

    def setUp(self):
        super().setUp()
        self.fb_state = os.path.join(self.tmp, "fb-posted.json")
        self.th_state = os.path.join(self.tmp, "threads-posted.json")
        self.reel_state = os.path.join(self.tmp, "reel-dist.json")
        self.files = []
        for n in (1, 2, 3):
            p = os.path.join(self.tmp, f"set-{n}.png")
            with open(p, "wb") as f:
                f.write(b"\x89PNG fake")
            self.files.append(p)
        self.fb_calls = []
        self.cli_cmds = []

        def fb_publish(text, url, image_url=None, image_path=None,
                       image_paths=None):
            self.fb_calls.append((image_paths, image_path))
            return {"state": "published", "post_url": "https://fb/s1"}

        def fake_run(cmd, **kw):
            self.cli_cmds.append(cmd)
            return mock.Mock(
                stdout=json.dumps({"post_id": "th-set"}), returncode=0)

        self._p = [
            mock.patch.object(fb_autopost, "STATE_FILE", self.fb_state),
            mock.patch.object(threads_autopost, "STATE_FILE",
                              self.th_state),
            mock.patch.object(flush, "REEL_STATE_FILE", self.reel_state),
            mock.patch.object(fb_autopost, "publish", fb_publish),
            mock.patch.object(flush.subprocess, "run", fake_run),
        ]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def _set_entry(self, channel, slug="set-story"):
        return make_entry(
            channel=channel, slug=slug, card_file=self.files[0],
            card_files=list(self.files),
            card_texts=["Set Story Headline", "The key takeaway.",
                        "Full story at thevideshi.com"],
            card_track="backdrop",
            image_url="https://img.example/hero.jpg")

    def test_fb_flush_attaches_whole_set_in_order(self):
        sq.add_entry(self._set_entry("facebook"))
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        self.assertEqual(self.fb_calls, [(self.files, None)])
        with open(self.fb_state) as f:
            self.assertEqual(json.load(f)["posted_slugs"], ["set-story"])

    def test_fb_set_hook_missing_degrades_to_hero(self):
        e = self._set_entry("facebook")
        e["card_files"] = [os.path.join(self.tmp, "gone-1.png"),
                           self.files[1], self.files[2]]
        e["card_file"] = e["card_files"][0]
        sq.add_entry(e)
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        # no image_paths, no image_path -> publish() hero behavior
        self.assertEqual(self.fb_calls, [(None, None)])

    def test_threads_flush_sends_ordered_media_items_with_alts(self):
        sq.add_entry(self._set_entry("threads"))
        with redirect_stdout(io.StringIO()):
            rc = flush.main()
        self.assertEqual(rc, 0)
        self.assertEqual(len(self.cli_cmds), 1)
        cmd = self.cli_cmds[0]
        idx = [i for i, a in enumerate(cmd) if a == "--media-item"]
        self.assertEqual(len(idx), 3)
        items = [json.loads(cmd[i + 1]) for i in idx]
        self.assertEqual([it["file"] for it in items], self.files)
        self.assertEqual([it["alt_text"] for it in items],
                         ["Set Story Headline", "The key takeaway.",
                          "Full story at thevideshi.com"])
        with open(self.th_state) as f:
            self.assertEqual(json.load(f)["post_ids"],
                             {"set-story": "th-set"})

    def test_list_annotates_set_size(self):
        sq.add_entry(self._set_entry("facebook"))
        with redirect_stdout(io.StringIO()) as buf:
            flush.print_list(sq.load_entries())
        self.assertIn("cards: set of 3 (backdrop)", buf.getvalue())


class TestFlushCliFailures(QueuePatchMixin, unittest.TestCase):
    """Regression (2026-10-24): the first Threads CARD SET flush
    stopped with 'threads article output not JSON: ' — the CLI
    had failed after its approval and the flush's stdout-only
    parsing destroyed the real error (stderr + exit code were
    captured and discarded). The flush's CLI wrappers now go
    through _run_cli_json: success needs exit 0 AND JSON, and
    failures surface stderr + exit code. The connector is mocked
    at the subprocess boundary — nothing here can post."""

    def setUp(self):
        super().setUp()
        self.th_state = os.path.join(self.tmp, "threads-posted.json")
        self.reel_state = os.path.join(self.tmp, "reel-dist.json")
        self.files = []
        for n in (1, 2, 3, 4):
            p = os.path.join(self.tmp, f"set-{n}.png")
            with open(p, "wb") as f:
                f.write(b"\x89PNG fake")
            self.files.append(p)
        self.cli_result = mock.Mock(stdout="", stderr="", returncode=1)
        self.cli_cmds = []

        def fake_run(cmd, **kw):
            self.cli_cmds.append(cmd)
            return self.cli_result

        self._p = [
            mock.patch.object(threads_autopost, "STATE_FILE",
                              self.th_state),
            mock.patch.object(flush, "REEL_STATE_FILE", self.reel_state),
            mock.patch.object(flush.subprocess, "run", fake_run),
        ]
        for p in self._p:
            p.start()

    def tearDown(self):
        for p in self._p:
            p.stop()
        super().tearDown()

    def _set_entry(self):
        return make_entry(
            channel="threads", slug="set-story",
            card_file=self.files[0], card_files=list(self.files),
            card_texts=["Set Story Headline", "Takeaway one.",
                        "Takeaway two.", "Full story at thevideshi.com"],
            card_track="backdrop",
            image_url="https://img.example/hero.jpg")

    def test_threads_set_success_via_helper(self):
        self.cli_result = mock.Mock(
            stdout=json.dumps({"post_id": "th-set4"}), stderr="",
            returncode=0)
        result = flush.publish_threads_article(self._set_entry())
        self.assertEqual(result, {"post_id": "th-set4"})
        cmd = self.cli_cmds[0]
        idx = [i for i, a in enumerate(cmd) if a == "--media-item"]
        self.assertEqual(len(idx), 4)
        items = [json.loads(cmd[i + 1]) for i in idx]
        self.assertEqual([it["file"] for it in items], self.files)
        self.assertEqual(items[3]["alt_text"],
                         "Full story at thevideshi.com")

    def test_threads_set_empty_stdout_surfaces_stderr(self):
        # The exact 2026-10-24 shape: CLI exits nonzero, stdout
        # empty, the real cause sitting on stderr.
        self.cli_result = mock.Mock(
            stdout="", returncode=1,
            stderr="Threads Write Rate Limit Reached")
        with redirect_stderr(io.StringIO()) as err:
            result = flush.publish_threads_article(self._set_entry())
        self.assertIsNone(result)
        self.assertIn("exit 1", err.getvalue())
        self.assertIn("Write Rate Limit", err.getvalue())

    def test_threads_set_exit0_empty_stdout_still_fails(self):
        self.cli_result = mock.Mock(stdout="", stderr="",
                                    returncode=0)
        with redirect_stderr(io.StringIO()) as err:
            result = flush.publish_threads_article(self._set_entry())
        self.assertIsNone(result)
        self.assertIn("exit 0", err.getvalue())

    def test_nonzero_exit_with_json_body_is_not_success(self):
        # An error JSON on stdout with a nonzero exit used to be
        # returned as a truthy "result" by the IG/FB-draft
        # wrappers — a false success. Now it must fail.
        self.cli_result = mock.Mock(
            stdout=json.dumps({"error": "nope"}), stderr="bad",
            returncode=2)
        with redirect_stderr(io.StringIO()):
            data = flush._run_cli_json(["cli"], "test call")
        self.assertIsNone(data)

    def test_flush_stops_and_keeps_set_queued_on_cli_failure(self):
        self.cli_result = mock.Mock(
            stdout="", returncode=1,
            stderr="carousel item upload failed")
        sq.add_entry(self._set_entry())
        with redirect_stdout(io.StringIO()) as out, \
                redirect_stderr(io.StringIO()) as err:
            rc = flush.main()
        self.assertEqual(rc, 1)
        self.assertIn("STOPPED", out.getvalue())
        self.assertIn("carousel item upload failed", err.getvalue())
        self.assertEqual(len(sq.load_entries()), 1)


import x_cards  # noqa: E402


class TestXCards(unittest.TestCase):
    """x-autopost's card-set attach: mocked generator + upload.
    All-or-nothing — any failure returns [] so x-autopost falls
    back to its hero image, exactly as before card sets."""

    ARTICLE = {"headline": "X Story", "category": "news",
               "image_url": "https://img.example/x.jpg",
               "key_takeaways": ["One.", "Two."],
               "subheadline": "Sub.", "slug": "x-story", "body": ""}

    def _gen(self, files, track="backdrop"):
        def gen(*a, **kw):
            return {"track": track, "files": files}
        return gen

    def test_uploads_set_in_order(self):
        files = ["/c/1.png", "/c/2.png", "/c/3.png", "/c/4.png"]
        ids = x_cards.card_set_media_ids(
            object(), self.ARTICLE, lambda p: p + ".jpg",
            lambda api, p: f"mid:{p}",
            generate_fn=self._gen(files))
        self.assertEqual(ids, [f"mid:/c/{n}.png.jpg" for n in (1, 2, 3, 4)])

    def test_caps_at_four(self):
        files = [f"/c/{n}.png" for n in range(1, 7)]
        ids = x_cards.card_set_media_ids(
            object(), self.ARTICLE, lambda p: p, lambda api, p: p,
            generate_fn=self._gen(files))
        self.assertEqual(len(ids), 4)

    def test_skipped_set_returns_empty(self):
        ids = x_cards.card_set_media_ids(
            object(), self.ARTICLE, lambda p: p, lambda api, p: p,
            generate_fn=self._gen([], track="skipped"))
        self.assertEqual(ids, [])

    def test_generation_failure_returns_empty(self):
        def boom(*a, **kw):
            raise RuntimeError("no render")
        ids = x_cards.card_set_media_ids(
            object(), self.ARTICLE, lambda p: p, lambda api, p: p,
            generate_fn=boom)
        self.assertEqual(ids, [])

    def test_upload_failure_abandons_set(self):
        calls = []

        def flaky(api, p):
            calls.append(p)
            if len(calls) == 2:
                raise RuntimeError("upload died")
            return f"mid:{p}"
        ids = x_cards.card_set_media_ids(
            object(), self.ARTICLE, lambda p: p, flaky,
            generate_fn=self._gen(["/c/1.png", "/c/2.png", "/c/3.png"]))
        self.assertEqual(ids, [])

    def test_no_image_never_generates(self):
        called = []
        article = dict(self.ARTICLE, image_url=None)
        ids = x_cards.card_set_media_ids(
            object(), article, lambda p: p, lambda api, p: p,
            generate_fn=lambda *a, **kw: called.append(1) or {})
        self.assertEqual(ids, [])
        self.assertEqual(called, [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
