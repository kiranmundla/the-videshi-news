#!/usr/bin/env python3
"""Batch convert markdown/plain-text article bodies to HTML.

Targets ALL published articles without </p> tags.
Uses curl for all Supabase calls. Processes in batches of 50.
"""
import json, os, re, subprocess, sys, time

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
BATCH_SIZE = 50
DRY_RUN = "--dry-run" in sys.argv


def inline_md(text):
    if not text:
        return text
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    text = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'(?<![<\w/])\*([^*]+)\*(?![>])', r'<em>\1</em>', text)
    return text


def md_to_html(body):
    if not body:
        return body
    lines = body.split('\n')
    result = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            result.append('')
            i += 1
            continue
        if stripped.startswith('<!--'):
            # Collect multi-line HTML comments
            if '-->' in stripped:
                result.append(line)
                i += 1
            else:
                comment_lines = [line]
                i += 1
                while i < len(lines) and '-->' not in lines[i]:
                    comment_lines.append(lines[i])
                    i += 1
                if i < len(lines):
                    comment_lines.append(lines[i])
                    i += 1
                result.extend(comment_lines)
            continue
        if stripped.startswith('<'):
            result.append(line)
            i += 1
            continue
        if re.match(r'^https?://\S+$', stripped):
            result.append(line)
            i += 1
            continue
        if stripped.startswith('#### '):
            result.append(f'<h4>{inline_md(stripped[5:].strip())}</h4>')
            i += 1
            continue
        if stripped.startswith('### '):
            result.append(f'<h3>{inline_md(stripped[4:].strip())}</h3>')
            i += 1
            continue
        if stripped.startswith('## '):
            result.append(f'<h2>{inline_md(stripped[3:].strip())}</h2>')
            i += 1
            continue
        if stripped.startswith('# '):
            result.append(f'<h2>{inline_md(stripped[2:].strip())}</h2>')
            i += 1
            continue
        if stripped.startswith('- ') or stripped.startswith('* '):
            items = []
            while i < len(lines) and (lines[i].strip().startswith('- ') or lines[i].strip().startswith('* ')):
                items.append(f'<li>{inline_md(lines[i].strip()[2:].strip())}</li>')
                i += 1
            result.append('<ul>' + ''.join(items) + '</ul>')
            continue
        if re.match(r'^\d+[\.\)]\s', stripped):
            items = []
            while i < len(lines) and re.match(r'^\d+[\.\)]\s', lines[i].strip()):
                item_text = re.sub(r'^\d+[\.\)]\s*', '', lines[i].strip())
                items.append(f'<li>{inline_md(item_text)}</li>')
                i += 1
            result.append('<ol>' + ''.join(items) + '</ol>')
            continue
        if stripped.startswith('> '):
            qlines = []
            while i < len(lines) and lines[i].strip().startswith('> '):
                qlines.append(inline_md(lines[i].strip()[2:].strip()))
                i += 1
            result.append('<blockquote>' + ' '.join(qlines) + '</blockquote>')
            continue
        para = []
        while i < len(lines):
            l = lines[i].strip()
            if not l or l.startswith('<') or l.startswith('<!--'):
                break
            if l.startswith('## ') or l.startswith('### ') or l.startswith('#### ') or l.startswith('# '):
                break
            if l.startswith('- ') or l.startswith('* ') or l.startswith('> '):
                break
            if re.match(r'^\d+[\.\)]\s', l) or re.match(r'^https?://\S+$', l):
                break
            para.append(l)
            i += 1
        if para:
            result.append(f'<p>{inline_md(" ".join(para))}</p>')
    return '\n'.join(result)


def fetch_batch():
    """Fetch next batch. Always offset=0 since converted articles drop out of filter."""
    url = (
        f"{SUPABASE_URL}/rest/v1/p2_articles"
        f"?status=eq.published"
        f"&body=not.like.*%3C%2Fp%3E*"   # no </p> tags
        f"&select=id,headline,body"
        f"&order=created_at.asc"
        f"&limit={BATCH_SIZE}"
    )
    r = subprocess.run(
        ["curl", "-s", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}"],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0 or not r.stdout.strip():
        return []
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return []


def patch_article(article_id, new_body):
    url = f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}"
    payload = json.dumps({"body": new_body})
    r = subprocess.run(
        ["curl", "-s", "-X", "PATCH", url,
         "-H", f"apikey: {SUPABASE_KEY}",
         "-H", f"Authorization: Bearer {SUPABASE_KEY}",
         "-H", "Content-Type: application/json",
         "-H", "Prefer: return=minimal",
         "-d", payload],
        capture_output=True, text=True, timeout=30
    )
    return r.returncode == 0 and "error" not in r.stdout.lower()


def main():
    total_converted = 0
    total_errors = 0
    total_unchanged = 0
    batch_num = 0
    consecutive_zero = 0

    mode = "[DRY RUN] " if DRY_RUN else ""
    print(f"{mode}Starting body → HTML batch conversion (all articles without </p>)")
    print(f"Batch size: {BATCH_SIZE}")
    sys.stdout.flush()

    while True:
        batch_num += 1
        articles = fetch_batch()

        if not articles:
            print(f"\n  No more articles. Done.")
            break

        converted_this = 0
        errors_this = 0
        unchanged_this = 0

        for a in articles:
            body = a.get("body", "")
            if not body or "</p>" in body:
                unchanged_this += 1
                continue

            new_body = md_to_html(body)
            if new_body == body:
                unchanged_this += 1
                continue

            if DRY_RUN:
                converted_this += 1
                continue

            if patch_article(a["id"], new_body):
                converted_this += 1
            else:
                errors_this += 1

        total_converted += converted_this
        total_errors += errors_this
        total_unchanged += unchanged_this

        print(f"  Batch {batch_num}: {converted_this} converted, {unchanged_this} unchanged | Total: {total_converted}")
        sys.stdout.flush()

        if converted_this == 0:
            consecutive_zero += 1
            if consecutive_zero >= 2:
                print(f"\n  No convertible articles in {consecutive_zero} consecutive batches. Stopping.")
                break
        else:
            consecutive_zero = 0

        if len(articles) < BATCH_SIZE:
            break
        time.sleep(0.3)

    print(f"\n{mode}Complete: {total_converted} converted, {total_unchanged} unchanged, {total_errors} errors")


if __name__ == "__main__":
    main()
