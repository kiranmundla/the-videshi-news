#!/usr/bin/env python3
"""Batch convert markdown article bodies to HTML.

Targets published articles with markdown ## headings and no </p> tags.
Uses curl for all Supabase calls (urllib fails through the proxy).
Processes in batches of 50, paginating through the full table.
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BATCH_SIZE = 50
DRY_RUN = "--dry-run" in sys.argv


def supabase_get(path, params=None):
    """GET from Supabase REST API via curl."""
    url = f"{SUPABASE_URL}/rest/v1/{path}"
    if params:
        url += "?" + "&".join(f"{k}={urllib.parse.quote(str(v), safe='.*!,')}" for k, v in params.items())
    result = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=30
    )
    return json.loads(result.stdout)


def supabase_patch(article_id, data):
    """PATCH a single article via curl."""
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = json.dumps(data)
    result = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    return result.returncode == 0 and "error" not in result.stdout.lower()


def md_to_html(body):
    """Convert markdown body to HTML.
    
    Rules:
    - ## heading → <h2>heading</h2>
    - ### heading → <h3>heading</h3>
    - #### heading → <h4>heading</h4>
    - **bold** → <strong>bold</strong>
    - *italic* → <em>italic</em>
    - [text](url) → <a href="url">text</a>
    - - list item → collected into <ul><li>...</li></ul>
    - Plain text paragraphs (separated by blank lines) → <p>text</p>
    - Lines starting with < (HTML) stay untouched
    - Bare URLs on their own line stay untouched (social embeds)
    - <!-- comments --> stay untouched
    """
    if not body:
        return body

    lines = body.split('\n')
    result = []
    i = 0

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Empty line — skip (paragraph breaks handled by grouping)
        if not stripped:
            result.append('')
            i += 1
            continue

        # HTML comments — pass through
        if stripped.startswith('<!--'):
            result.append(line)
            i += 1
            continue

        # Already HTML (starts with <) — pass through
        if stripped.startswith('<'):
            result.append(line)
            i += 1
            continue

        # Bare URLs on their own line (social embeds, images) — pass through
        if re.match(r'^https?://\S+$', stripped):
            result.append(line)
            i += 1
            continue

        # Markdown headings
        if stripped.startswith('#### '):
            heading_text = inline_md(stripped[5:].strip())
            result.append(f'<h4>{heading_text}</h4>')
            i += 1
            continue
        if stripped.startswith('### '):
            heading_text = inline_md(stripped[4:].strip())
            result.append(f'<h3>{heading_text}</h3>')
            i += 1
            continue
        if stripped.startswith('## '):
            heading_text = inline_md(stripped[3:].strip())
            result.append(f'<h2>{heading_text}</h2>')
            i += 1
            continue

        # List items — collect consecutive items into <ul>
        if stripped.startswith('- ') or stripped.startswith('* '):
            list_items = []
            while i < len(lines) and lines[i].strip().startswith(('- ', '* ')):
                item_text = inline_md(lines[i].strip()[2:].strip())
                list_items.append(f'<li>{item_text}</li>')
                i += 1
            result.append('<ul>' + ''.join(list_items) + '</ul>')
            continue

        # Numbered list items
        if re.match(r'^\d+[\.\)]\s', stripped):
            list_items = []
            while i < len(lines) and re.match(r'^\d+[\.\)]\s', lines[i].strip()):
                item_text = re.sub(r'^\d+[\.\)]\s*', '', lines[i].strip())
                item_text = inline_md(item_text)
                list_items.append(f'<li>{item_text}</li>')
                i += 1
            result.append('<ol>' + ''.join(list_items) + '</ol>')
            continue

        # Blockquotes
        if stripped.startswith('> '):
            quote_lines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                quote_lines.append(inline_md(lines[i].strip()[2:].strip()))
                i += 1
            result.append('<blockquote>' + ' '.join(quote_lines) + '</blockquote>')
            continue

        # Regular paragraph — collect consecutive non-empty text lines
        para_lines = []
        while i < len(lines):
            l = lines[i].strip()
            if not l:
                break
            if l.startswith('<') or l.startswith('<!--'):
                break
            if l.startswith('## ') or l.startswith('### ') or l.startswith('#### '):
                break
            if l.startswith('- ') or l.startswith('* '):
                break
            if re.match(r'^\d+[\.\)]\s', l):
                break
            if l.startswith('> '):
                break
            if re.match(r'^https?://\S+$', l):
                break
            para_lines.append(l)
            i += 1

        if para_lines:
            para_text = inline_md(' '.join(para_lines))
            result.append(f'<p>{para_text}</p>')
        continue

    return '\n'.join(result)


def inline_md(text):
    """Convert inline markdown: bold, italic, links."""
    if not text:
        return text
    # Links: [text](url)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    # Bold: **text**
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    # Italic: *text* (but not inside URLs or already-processed tags)
    text = re.sub(r'(?<![<\w/])\*([^*]+)\*(?![>])', r'<em>\1</em>', text)
    return text


def main():
    total_converted = 0
    total_errors = 0
    offset = 0

    print(f"{'[DRY RUN] ' if DRY_RUN else ''}Starting markdown → HTML batch conversion")
    print(f"Batch size: {BATCH_SIZE}")
    print()

    while True:
        # Fetch batch: published articles with ## headings, no </p> tags
        articles = supabase_get("p2_articles", {
            "status": "eq.published",
            "body": "not.like.*</p>*",
            "select": "id,headline,body",
            "order": "created_at.asc",
            "limit": BATCH_SIZE,
            "offset": offset,
        })

        if not articles:
            break

        # Filter for actual markdown (has ## headings)
        md_articles = [a for a in articles if a.get("body") and "\n## " in a["body"]]

        if not md_articles and len(articles) < BATCH_SIZE:
            # No more articles with ## headings and we've exhausted the results
            break

        if not md_articles:
            offset += BATCH_SIZE
            continue

        batch_converted = 0
        for article in md_articles:
            aid = article["id"]
            headline = article["headline"][:60] if article.get("headline") else "?"
            body = article["body"]

            # Convert
            new_body = md_to_html(body)

            # Sanity check: new body should have some HTML
            if new_body == body:
                continue

            if DRY_RUN:
                batch_converted += 1
                continue

            # Patch
            if supabase_patch(aid, {"body": new_body}):
                batch_converted += 1
            else:
                total_errors += 1
                print(f"  ❌ Failed: {headline}", file=sys.stderr)

        total_converted += batch_converted
        print(f"  Batch at offset {offset}: {batch_converted}/{len(md_articles)} converted (total: {total_converted})")

        # If this batch had fewer than BATCH_SIZE, we're done
        if len(articles) < BATCH_SIZE:
            break

        offset += BATCH_SIZE
        # Small delay to avoid hammering the API
        time.sleep(0.5)

    print(f"\n{'[DRY RUN] ' if DRY_RUN else ''}Done: {total_converted} articles converted, {total_errors} errors")


if __name__ == "__main__":
    main()
