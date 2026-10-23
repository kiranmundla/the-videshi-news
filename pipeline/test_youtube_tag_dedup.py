"""Regression tests: URL-form <youtube> tags must dedup like bare-ID tags.

Real failure (2026-10-22): the Sacramento ICE/murder article carried
<youtube>https://youtube.com/watch?v=9mDdfA6l0HY</youtube> in the body AND
the same video in social_embeds, so it rendered twice. Three bare-ID-only
regexes missed it:
  - enrich-on-publish promote_inline_social_urls promoted the watch URL
    found *inside* the tag into social_embeds,
  - enrich-on-publish Fix 3 dedup extracted tag IDs with a bare-ID regex,
  - review-articles check_duplicate_embeds used the same regex.
The frontend (YouTubeEmbed.extractYouTubeId) accepts both tag forms.

Run: python3 test_youtube_tag_dedup.py  (exit 0 = all pass)
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
fails = 0
total = 0


def check(name, cond, extra=""):
    global fails, total
    total += 1
    if cond:
        print(f"ok   {name}")
    else:
        fails += 1
        print(f"FAIL {name} {extra}")


def load(name, fn):
    spec = importlib.util.spec_from_file_location(name, os.path.join(HERE, fn))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


rev = load("review_articles", "review-articles.py")
enr = load("enrich_on_publish", "enrich-on-publish.py")

VID = "9mDdfA6l0HY"
EMB = [{"url": f"https://www.youtube.com/watch?v={VID}",
        "type": "youtube", "video_id": VID}]

# Reviewer: duplicate detection
check("reviewer flags URL-form tag dup",
      len(rev.check_duplicate_embeds(
          {"body": f"<p>x</p>\n<youtube>https://youtube.com/watch?v={VID}</youtube>",
           "social_embeds": EMB})) == 1)
check("reviewer flags bare-ID tag dup",
      len(rev.check_duplicate_embeds(
          {"body": f"<youtube>{VID}</youtube>", "social_embeds": EMB})) == 1)
check("reviewer flags youtu.be-form tag dup",
      len(rev.check_duplicate_embeds(
          {"body": f"<youtube>https://youtu.be/{VID}</youtube>",
           "social_embeds": EMB})) == 1)
check("reviewer does NOT flag href-buried URL",
      rev.check_duplicate_embeds(
          {"body": f'<p><a href="https://www.youtube.com/watch?v={VID}">x</a></p>',
           "social_embeds": EMB}) == [])
check("reviewer does NOT flag embed with no inline copy",
      rev.check_duplicate_embeds(
          {"body": "<p>hi</p>", "social_embeds": EMB}) == [])

# Enricher: promotion must not harvest URLs from inside <youtube> tags
check("promote skips URL-form tag", enr.promote_inline_social_urls(
    f"<p>x</p>\n<youtube>https://youtube.com/watch?v={VID}</youtube>", []) == ([], 0))
check("promote skips youtu.be-form tag", enr.promote_inline_social_urls(
    f"<youtube>https://youtu.be/{VID}</youtube>", []) == ([], 0))
check("promote skips bare-ID tag", enr.promote_inline_social_urls(
    f"<youtube>{VID}</youtube>", []) == ([], 0))
_out, _n = enr.promote_inline_social_urls(
    f"<p>see https://www.youtube.com/watch?v={VID} now</p>", [])
check("promote still harvests a plain body watch URL", _n == 1 and _out[0]["video_id"] == VID)

print(f"\n{total - fails}/{total} passed")
sys.exit(1 if fails else 0)
