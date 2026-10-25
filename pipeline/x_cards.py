#!/usr/bin/env python3
"""Card-set attach helper for x-autopost.py.

Kiran's format map (2026-10-24): X carries CARD CAROUSELS. At post
time the article's social card set (social_card.make_card_set —
hook + key-takeaway cards + closer) is generated and up to 4 cards
(X's image cap) upload through x-autopost's existing media path.

All-or-nothing: if the set is skipped (<600px hero), generation
fails, or ANY upload fails, this returns [] and the caller falls
back to today's behavior (the prebuilt-reel carousel check, then
the single hero image, then text-only) — a partial set never goes
out half-attached.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

MAX_X_IMAGES = 4


def card_set_media_ids(api_v1, article, compress_fn, upload_fn,
                       generate_fn=None, limit=MAX_X_IMAGES):
    """Generate the article's card set and upload up to `limit`
    cards, in set order. Returns the X media_ids ([] on any
    failure — see module docstring).

    compress_fn / upload_fn are x-autopost's own helpers
    (compress_for_upload / upload_image_file), injected so this
    stays unit-testable without touching X. generate_fn defaults
    to social_card.make_card_set."""
    if not article.get("image_url"):
        return []
    if generate_fn is None:
        import social_card
        generate_fn = social_card.make_card_set
    try:
        info = generate_fn(
            article.get("headline"), article.get("category"),
            image_url=article.get("image_url"),
            key_takeaways=article.get("key_takeaways"),
            subheadline=article.get("subheadline"),
            slug=article.get("slug"),
            body=article.get("body"))
    except Exception as e:
        print(f"    card set generation failed: {e}")
        return []
    if not info or info.get("track") == "skipped":
        return []
    files = (info.get("files") or [])[:limit]
    if not files:
        return []
    media_ids = []
    for path in files:
        up_path = None
        try:
            up_path = compress_fn(path)
            media_ids.append(upload_fn(api_v1, up_path))
        except Exception as e:
            print(f"    card upload failed ({e}); abandoning set")
            return []
        finally:
            # compress_fn returns a fresh temp file on success and
            # the source path itself on failure — only ever delete
            # the temp copy, never the rendered card.
            if up_path and up_path != path:
                try:
                    os.unlink(up_path)
                except Exception:
                    pass
    return media_ids
