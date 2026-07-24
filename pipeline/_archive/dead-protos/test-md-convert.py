#!/usr/bin/env python3
"""Test the markdown → HTML conversion on a single article."""
import json, subprocess, os, re

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

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
            result.append(line)
            i += 1
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
            if not l or l.startswith('<') or l.startswith('<!--') or l.startswith('## ') or l.startswith('### ') or l.startswith('#### ') or l.startswith('- ') or l.startswith('* ') or l.startswith('> ') or re.match(r'^\d+[\.\)]\s', l) or re.match(r'^https?://\S+$', l):
                break
            para.append(l)
            i += 1
        if para:
            result.append(f'<p>{inline_md(" ".join(para))}</p>')
    return '\n'.join(result)

# Fetch one article
url = f'{SUPABASE_URL}/rest/v1/p2_articles?status=eq.published&select=id,headline,body&order=created_at.desc&limit=1'
url += '&body=like.*%23%23%20*&body=not.like.*%3C%2Fp%3E*'
r = subprocess.run(['curl', '-s', url, '-H', f'apikey: {SUPABASE_KEY}', '-H', f'Authorization: Bearer {SUPABASE_KEY}'], capture_output=True, text=True, timeout=30)
articles = json.loads(r.stdout)
a = articles[0]

print(f'Headline: {a["headline"][:60]}')
print(f'=== BEFORE ({len(a["body"])} chars) ===')
print(a['body'][:500])
print('\n...\n')

converted = md_to_html(a['body'])
print(f'=== AFTER ({len(converted)} chars) ===')
print(converted[:500])
print('\n...\n')

print(f'Has </p>: {"</p>" in converted}')
print(f'Has <h2>: {"<h2>" in converted}')
print(f'Still has ## : {chr(10) + "## " in converted}')
has_dc = "vdc-takeaways" in a["body"]
print(f'Data cards preserved: {"vdc-takeaways" in converted if has_dc else "N/A (no data cards)"}')
