#!/usr/bin/env python3
"""
Flush the delayed-publish social queue — run ONLY while Kiran is
present: every publish below makes a connector call that needs his
fresh approval at call time. That is the whole point of the queue
(fb-autopost.py / threads-autopost.py / reel-distribute-social.py
stage fully-ready entries on schedule with zero connector calls;
this script publishes them).

Usage:
  python3 -u social-publish-flush.py --list   # show the queue, publish nothing
  python3 -u social-publish-flush.py          # publish in created order

Env: .env.supabase sourced by the caller (ledger writes mirror the
producer scripts exactly).

Behavior:
  * Publishes strictly in created order (a Facebook article always
    precedes its Threads mirror, which was staged later).
  * On each success: writes the channel ledger exactly as the
    producer script's immediate mode does (fb-posted.json /
    threads-posted.json / reel-distribution.json + the prebuilt_reels
    IG stamp), then removes the entry from the queue.
  * Article entries with a staged social CARD SET (card_files:
    hook + takeaway cards + closer) publish the whole set: FB
    attaches every card to the Page post (facebook-cli --file
    repeats in post order), Threads carries every card as an
    ordered media item with its own alt text. Entries with only a
    single card (card_file, incl. Instagram article entries, which
    stay single-card) publish that card as the image. Entries
    without a card publish exactly as before cards existed.
  * A queue entry whose slug is already in the published ledger
    (e.g. posted via a manual --publish-now run) is dropped as done.
  * On the FIRST failure or declined approval: stops, keeps that
    entry and everything after it queued, prints a summary, exit 1.
"""
import json
import os
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import social_queue  # noqa: E402

LIST_ONLY = "--list" in sys.argv

PIPELINE = os.path.expanduser("~/workspace/the-videshi-news/pipeline")
REEL_STATE_FILE = os.path.join(PIPELINE, ".state/reel-distribution.json")
PAGE_ID = "1243823795489375"
IG_ACCOUNT_ID = "17841426005310230"       # @the.videshi
THREADS_ACCOUNT_ID = "17841436385342619"   # @the.videshi
FB_CLI = "/opt/hatch/bin/facebook-cli"
IG_CLI = "/opt/hatch/bin/instagram-cli"
THREADS_CLI = "/opt/hatch/bin/threads-cli"
FB_DRAFT_TEXT_LIMIT = 1024  # drafts are created with the staged text
                            # verbatim (already trimmed at stage time)


def _run_cli_json(cmd, label, timeout=600):
    """Run a connector CLI and parse its JSON stdout.

    Success requires BOTH a zero exit code and parseable JSON —
    the CLIs report their real errors on stderr (validation
    rejects, rate limits, a carousel item failing mid-upload
    after the approval), and a wrapper that only looks at stdout
    turns every such failure into a content-free "output not
    JSON: " with the actual cause destroyed (2026-10-24: the
    first Threads card-set flush stopped exactly this way).
    On failure this prints the exit code, stdout AND stderr, and
    returns None; the caller stops the flush with the entry still
    queued. A publish that fails after its approval is AMBIGUOUS
    per the connector docs (the post may or may not exist), so
    the message says to verify on the channel before re-running.
    """
    r = subprocess.run(cmd, capture_output=True, text=True,
                       timeout=timeout)
    data = None
    if isinstance(r.stdout, str) and r.stdout.strip():
        try:
            data = json.loads(r.stdout)
        except json.JSONDecodeError:
            data = None
    if r.returncode == 0 and data is not None:
        return data
    out = r.stdout if isinstance(r.stdout, str) else ""
    err = r.stderr if isinstance(r.stderr, str) else ""
    print(f"ERROR: {label} failed (exit {r.returncode}): "
          f"stdout={out[:200]!r} stderr={err[:400]!r} — if this "
          f"was a publish, the outcome is ambiguous; verify on "
          f"the channel before re-running.", file=sys.stderr)
    return None


# ------------------------------------------------------------------
# Producer modules use hyphenated filenames (fb-autopost.py), so
# they are loaded by path rather than imported by name.
# ------------------------------------------------------------------

_MODULES = {}


def _producer(mod_name, filename):
    if mod_name not in _MODULES:
        if mod_name in sys.modules:  # already loaded (e.g. by tests)
            _MODULES[mod_name] = sys.modules[mod_name]
            return _MODULES[mod_name]
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            mod_name, os.path.join(PIPELINE, filename))
        mod = importlib.util.module_from_spec(spec)
        sys.modules[mod_name] = mod
        spec.loader.exec_module(mod)
        _MODULES[mod_name] = mod
    return _MODULES[mod_name]


def _fb():
    return _producer("fb_autopost", "fb-autopost.py")


def _th():
    return _producer("threads_autopost", "threads-autopost.py")


# ------------------------------------------------------------------
# Publish dispatchers — CLI invocations mirror the producer scripts.
# ------------------------------------------------------------------

def _existing_set_files(entry):
    """The entry's staged card-set files that still exist on disk,
    in set order. The set is only usable when its hook (first
    file) survives — a partial set missing a middle degrades to
    the surviving cards; a missing hook degrades to []."""
    files = [f for f in (entry.get("card_files") or []) if f]
    if not files or not os.path.exists(files[0]):
        return []
    return [f for f in files if os.path.exists(f)]


def publish_fb_article(entry):
    # With a staged card SET, ALL cards attach to the Page post
    # (fb publish() passes them as repeated --file, in post order,
    # and never deletes caller-owned files). With only a single
    # card, that card is the attached image. Without either — or
    # if the files have gone missing since staging — today's
    # plain-hero attach, unchanged.
    files = _existing_set_files(entry)
    if files:
        return _fb().publish(entry["text"], entry.get("link"),
                             entry.get("image_url"), image_paths=files)
    card = entry.get("card_file")
    if card and os.path.exists(card):
        return _fb().publish(entry["text"], entry.get("link"),
                             entry.get("image_url"), image_path=card)
    return _fb().publish(entry["text"], entry.get("link"),
                         entry.get("image_url"))


def publish_threads_article(entry):
    # With a staged card SET, every card rides as an ordered media
    # item with its own alt text (hook = headline, middles = their
    # takeaway, closer = the full-story line) — the same
    # --media-item mechanism as reel posts, repeated 1-20x in
    # display order (images take no cover). With only a single
    # card, that one item. Without either, the text-only publish,
    # unchanged.
    files = _existing_set_files(entry)
    single = entry.get("card_file")
    if not files and single and os.path.exists(single):
        files = [single]
    if files:
        texts = entry.get("card_texts") or []
        cmd = [THREADS_CLI, "publish-post", "--account-id",
               THREADS_ACCOUNT_ID, "--text", entry["text"]]
        for i, path in enumerate(files):
            item = {"file": path}
            alt = texts[i] if i < len(texts) else None
            if not alt and i == 0:
                alt = entry.get("headline")
            if alt:
                item["alt_text"] = str(alt)[:1024]
            cmd += ["--media-item", json.dumps(item)]
        return _run_cli_json(cmd, "threads article publish")
    return _th().publish(entry["text"])


def publish_ig_article(entry):
    """instagram-cli post-feed with the staged card as a photo post
    — the same command the reel path uses. Per the Instagram
    connector doc, one JPEG/PNG (preferably 1080x1350, exactly the
    card's size) publishes a photo post, and images take no
    --cover."""
    cmd = [IG_CLI, "post-feed", "--account-id", IG_ACCOUNT_ID,
           "--file", entry["card_file"], "--caption", entry["text"]]
    return _run_cli_json(cmd, "ig article post")


def create_fb_reel_draft(entry):
    """facebook-cli pages drafts create — mirrors
    reel-distribute-social.py's fb_draft() (text was trimmed to the
    FB draft limit at stage time)."""
    cmd = [FB_CLI, "pages", "drafts", "create", "--page-id", PAGE_ID,
           "--text", entry["text"], "--file", entry["media_file"]]
    data = _run_cli_json(cmd, "fb draft create")
    if data is None:
        return None
    return data.get("draft_id") or data.get("id") or data


def publish_ig_reel(entry):
    """instagram-cli post-feed — mirrors reel-distribute-social.py's
    ig_post()."""
    cmd = [IG_CLI, "post-feed", "--account-id", IG_ACCOUNT_ID,
           "--file", entry["media_file"], "--caption", entry["text"]]
    if entry.get("cover_file"):
        cmd += ["--cover", entry["cover_file"]]
    return _run_cli_json(cmd, "ig reel post")


def publish_threads_reel(entry):
    """threads-cli publish-post — mirrors reel-distribute-social.py's
    threads_post(); the media item also carries the staged alt_text
    (supported by the CLI and required final at stage time)."""
    item = {"file": entry["media_file"]}
    if entry.get("cover_file"):
        item["cover"] = entry["cover_file"]
    if entry.get("alt_text"):
        item["alt_text"] = entry["alt_text"]
    cmd = [THREADS_CLI, "publish-post", "--account-id", THREADS_ACCOUNT_ID,
           "--text", entry["text"], "--media-item", json.dumps(item)]
    return _run_cli_json(cmd, "threads reel post")


# ------------------------------------------------------------------
# Ledger writes — exactly as the producer scripts record success.
# ------------------------------------------------------------------

def load_reel_state():
    try:
        with open(REEL_STATE_FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_reel_state(state):
    os.makedirs(os.path.dirname(REEL_STATE_FILE), exist_ok=True)
    with open(REEL_STATE_FILE, "w") as f:
        json.dump(state, f, indent=1)


def sb_patch(path, payload):
    url = f"{os.environ['SUPABASE_URL']}/rest/v1/{path}"
    key = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
    cmd = ["curl", "-s", "-X", "PATCH", url,
           "-H", f"apikey: {key}",
           "-H", f"Authorization: Bearer {key}",
           "-H", "Content-Type: application/json",
           "-H", "Prefer: return=minimal",
           "-d", json.dumps(payload)]
    subprocess.run(cmd, capture_output=True, text=True, timeout=30)


def already_published(entry):
    """True when the channel ledger already records this entry —
    drop it as done instead of double-posting."""
    kind, channel = entry.get("kind"), entry.get("channel")
    if kind == "article_post" and channel == "facebook":
        posted, _p, _a, _s = _fb().load_posted()
        return entry.get("slug") in posted
    if kind == "article_post" and channel == "threads":
        state = _th().load_state()
        return bool(state) and entry.get("slug") in state[0]
    if kind == "article_post" and channel == "instagram":
        # No IG article ledger — the queue entry itself is the
        # record (removed on publish), and re-staging is prevented
        # upstream because a published FB pick leaves the picker.
        return False
    if kind == "reel_draft" and channel == "facebook":
        return bool(load_reel_state().get(entry.get("reel_id") or "", {})
                    .get("fb_draft_id"))
    if kind == "reel_post" and channel == "instagram":
        return bool(load_reel_state().get(entry.get("reel_id") or "", {})
                    .get("ig_done"))
    if kind == "reel_post" and channel == "threads":
        return bool(load_reel_state().get(entry.get("reel_id") or "", {})
                    .get("threads_post_id"))
    return False


def record_success(entry, result):
    """Write the ledger(s) for a successful publish; return a short
    result id for the summary."""
    kind, channel = entry.get("kind"), entry.get("channel")
    if kind == "article_post" and channel == "facebook":
        fb = _fb()
        posted, pending, abandoned, pending_since = fb.load_posted()
        posted.add(entry["slug"])
        fb.save_posted(posted, pending, abandoned, pending_since)
        return result.get("post_url") or result.get("post_id") or "ok"
    if kind == "article_post" and channel == "threads":
        th = _th()
        state = th.load_state()
        if state is None:
            state = (set(), set(), set(), {}, {})
        posted, pending, abandoned, pending_since, post_ids = state
        posted.add(entry["slug"])
        post_ids[entry["slug"]] = result["post_id"]
        th.save_state(posted, pending, abandoned,
                      pending_since, post_ids)
        return result["post_id"]
    if kind == "article_post" and channel == "instagram":
        # No IG article ledger (see already_published) — the queue
        # removal in main() is the record of the publish.
        return str(result.get("post_id") or result.get("id") or "ok")
    state = load_reel_state()
    rent = state.setdefault(entry["reel_id"], {})
    if kind == "reel_draft" and channel == "facebook":
        rent["fb_draft_id"] = str(result)
        save_reel_state(state)
        return str(result)
    if kind == "reel_post" and channel == "instagram":
        rent["ig_done"] = True
        rent["ig_result"] = result.get("post_id") or result.get("id")
        save_reel_state(state)
        if entry.get("reel_row_id"):
            from datetime import timezone
            sb_patch(f"prebuilt_reels?id=eq.{entry['reel_row_id']}",
                     {"ig_media_id": str(rent["ig_result"] or ""),
                      "ig_posted_at": datetime.now(timezone.utc)
                      .isoformat()})
        return str(rent["ig_result"])
    if kind == "reel_post" and channel == "threads":
        rent["threads_post_id"] = result["post_id"]
        save_reel_state(state)
        return result["post_id"]
    return "ok"


def dispatch(entry):
    """Returns the publish result (truthy) or None on failure."""
    kind, channel = entry.get("kind"), entry.get("channel")
    if kind in ("reel_draft", "reel_post"):
        media = entry.get("media_file")
        if not media or not os.path.exists(media):
            print(f"ERROR: media file missing for {entry.get('id')}: "
                  f"{media}", file=sys.stderr)
            return None
    if (channel, kind) == ("facebook", "article_post"):
        return publish_fb_article(entry)
    if (channel, kind) == ("threads", "article_post"):
        result = publish_threads_article(entry)
        return result if result and result.get("post_id") else None
    if (channel, kind) == ("instagram", "article_post"):
        # IG is card-only: the card IS the post. A card file that
        # has gone missing since staging is a hard stop, exactly
        # like a missing reel media file above.
        card = entry.get("card_file")
        if not card or not os.path.exists(card):
            print(f"ERROR: card file missing for IG article entry "
                  f"{entry.get('id')}: {card}", file=sys.stderr)
            return None
        result = publish_ig_article(entry)
        return result if result else None
    if (channel, kind) == ("facebook", "reel_draft"):
        result = create_fb_reel_draft(entry)
        return result if result else None
    if (channel, kind) == ("instagram", "reel_post"):
        result = publish_ig_reel(entry)
        return result if result else None
    if (channel, kind) == ("threads", "reel_post"):
        result = publish_threads_reel(entry)
        return result if result and result.get("post_id") else None
    print(f"ERROR: unknown queue entry kind: {channel}/{kind}",
          file=sys.stderr)
    return None


# ------------------------------------------------------------------

def entry_label(entry):
    name = (entry.get("headline") or entry.get("slug")
            or entry.get("reel_id") or entry.get("id"))
    return f"[{entry.get('channel')}/{entry.get('kind')}] {name}"


def card_annotation(entry):
    """'cards: set of N (track)' / 'card: …' / 'card: none…' for
    article entries, so the flush sitting shows exactly what
    images will go out."""
    if entry.get("kind") != "article_post":
        return ""
    files = entry.get("card_files") or []
    if len(files) > 1:
        return (f" · cards: set of {len(files)} "
                f"({entry.get('card_track') or 'rendered'})")
    if entry.get("card_file"):
        return f" · card: {entry.get('card_track') or 'rendered'}"
    if entry.get("card_track") == "skipped":
        return " · card: none (<600px skip)"
    return " · card: none"


def print_list(entries):
    if not entries:
        print("Publish queue is empty.")
        return
    print(f"Publish queue — {len(entries)} entr"
          f"{'y' if len(entries) == 1 else 'ies'} (created order):")
    for i, entry in enumerate(entries, 1):
        age = social_queue.age_hours(entry)
        age_txt = f"{age:.1f}h old" if age is not None else "age ?"
        stale = " — STALE (>48h)" if social_queue.is_stale(entry) else ""
        print(f"{i}. {entry_label(entry)} — {age_txt}{stale}"
              f"{card_annotation(entry)}")
        print(f"   staged {entry.get('created_at')} "
              f"via {entry.get('source')}")


def _created_ts(entry):
    try:
        dt = datetime.fromisoformat(entry.get("created_at") or "")
        return dt.timestamp()
    except Exception:
        return 0.0


def main():
    entries = sorted(social_queue.load_entries(), key=_created_ts)
    if LIST_ONLY:
        print_list(entries)
        return 0
    if not entries:
        print("Publish queue is empty — nothing to flush.")
        return 0
    print(f"Flushing {len(entries)} queued item(s) in created order. "
          f"Each publish needs Kiran's approval as it fires.")
    published = []
    for entry in entries:
        label = entry_label(entry)
        if already_published(entry):
            social_queue.remove_entry(entry["id"])
            print(f"Already published per ledger — dropped: {label}")
            published.append((label, "already-published"))
            continue
        print(f"Publishing: {label}")
        try:
            result = dispatch(entry)
        except Exception as e:  # connector error, timeout, etc.
            result = None
            print(f"ERROR: publish raised: {e}", file=sys.stderr)
        if not result:
            remaining = len(social_queue.load_entries())
            print(f"\nSTOPPED at: {label}")
            print(f"Published this flush: {len(published)}")
            for lbl, rid in published:
                print(f"  ✓ {lbl} -> {rid}")
            print(f"Still queued (incl. the failed entry): {remaining}")
            return 1
        rid = record_success(entry, result)
        social_queue.remove_entry(entry["id"])
        published.append((label, rid))
        print(f"  ✓ {label} -> {rid}")
    print(f"\nFlush complete: {len(published)} published, queue empty.")
    for lbl, rid in published:
        print(f"  ✓ {lbl} -> {rid}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
