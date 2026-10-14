#!/usr/bin/env python3
"""RETIRED 2026-10-14 — do not resurrect.

This file was the legacy bulk YouTube Shorts uploader. It uploaded up to 2
reels per run as PUBLIC videos with no quality gate and no write-back to
prebuilt_reels; on Oct 9–12 2026 it auto-published unapproved Shorts
(Kiran's catch, 2026-10-12), after which its cron was disabled and the
publish model was locked: unlisted-only, human flips public.

The original code is preserved at upload-youtube-shorts.py.RETIRED for
forensic reference only. The single sanctioned publish path is now:

    python3 -u reel_publish.py --verdict <reel_produce.py verdict.json>

which refuses anything without a full fact-check + frame-QA PASS and can
only ever upload as UNLISTED (privacy is a module-level constant there).

This stub exists so any stale reference (an old cron body, a doc, muscle
memory) fails loudly instead of publishing. It takes no action, ever.
"""

import sys

MESSAGE = (
    "REFUSED: upload-youtube-shorts.py was retired on 2026-10-14.\n"
    "It uploaded PUBLIC Shorts with no gate and no write-back.\n"
    "Use the sanctioned path instead:\n"
    "  python3 -u reel_publish.py --verdict <verdict.json>   (unlisted only)\n"
    "Original code: upload-youtube-shorts.py.RETIRED (forensic reference)."
)


def main():
    print(MESSAGE, file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
