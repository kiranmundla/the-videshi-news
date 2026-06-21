#!/usr/bin/env python3
"""
image-sync-audit.py — Detect articles whose HERO image does not match the story.

Uses GPT-4o vision to look at each recent article's hero image and judge whether
it plausibly belongs to the headline/subject. Flags clear mismatches (e.g. a band
photo on a shipping story, a wrong-person photo, a generic stock image that
contradicts the subject).

This complements the deterministic inline-image guard in enrich-articles.py
(which only catches the Wikipedia title-case-phrase failure). This pass catches
visual mismatches the rules can't see, on the hero image specifically.

Usage:
  python3 image-sync-audit.py                 # scan, report only (default 60 newest)
  python3 image-sync-audit.py --limit 120     # scan more
  python3 image-sync-audit.py --since-days 2  # only articles created in last N days
  python3 image-sync-audit.py --json out.json # write machine-readable report

Read-only: never patches the DB. Surfaces a list for human/agent review.
"""
import os, sys, json, re, base64, argparse, time
import requests

PIPELINE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))

load_env(os.path.expanduser('~/workspace/.env.supabase'))
load_env(os.path.expanduser('~/workspace/.env.openai'))

U = os.environ['SUPABASE_URL']
K = os.environ['SUPABASE_SERVICE_ROLE_KEY']
OAI = os.environ['OPENAI_API_KEY']
H = {'apikey': K, 'Authorization': f'Bearer {K}'}

session = requests.Session()

def fetch_articles(limit, since_days):
    params = {
        'select': 'slug,headline,subheadline,category,image_url,image_caption,created_at',
        'order': 'created_at.desc',
        'limit': str(limit),
        'image_url': 'not.is.null',
    }
    if since_days:
        import datetime
        cutoff = (datetime.datetime.utcnow() - datetime.timedelta(days=since_days)).isoformat()
        params['created_at'] = f'gte.{cutoff}'
    r = session.get(f'{U}/rest/v1/p2_articles', headers=H, params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def download_image_b64(url):
    """Download an image, return (b64, mime) or (None, None). Uses curl fallback
    for Wikimedia (Python requests can 429)."""
    try:
        r = session.get(url, headers={'User-Agent': 'TheVideshi/1.0 (thevideshi.com)'}, timeout=20)
        if r.status_code == 200 and r.content:
            mime = r.headers.get('Content-Type', 'image/jpeg').split(';')[0]
            if not mime.startswith('image/'):
                mime = 'image/jpeg'
            return base64.b64encode(r.content).decode(), mime
    except Exception:
        pass
    # curl fallback (proxy + 429-resistant)
    try:
        import subprocess
        tmp = '/tmp/_audit_img'
        subprocess.run(['curl', '-sS', '-A', 'TheVideshi/1.0 (thevideshi.com)',
                        '-o', tmp, url], timeout=30, check=True)
        if os.path.exists(tmp) and os.path.getsize(tmp) > 0:
            with open(tmp, 'rb') as f:
                data = f.read()
            return base64.b64encode(data).decode(), 'image/jpeg'
    except Exception:
        pass
    return None, None

JUDGE_PROMPT = """You are a photo desk editor for an Indian-diaspora news site. \
You are shown ONE photo and the headline/subject it was attached to. Decide whether \
the photo plausibly belongs to this story.

Headline: {headline}
Subheadline: {subheadline}
Category: {category}
Caption on the photo: {caption}

Judge ONLY gross mismatches. A photo is a MISMATCH if it clearly depicts a different \
subject than the story — e.g. a music album cover / band on a non-music story, the \
wrong named person, an unrelated logo, a meme, or an image whose subject contradicts \
the headline. A generic-but-on-topic photo (a stock oil tanker for a shipping story, \
a city skyline for a city story) is a MATCH, not a mismatch. When unsure, say MATCH.

Reply with strict JSON only:
{{"verdict":"MATCH"|"MISMATCH","what_photo_shows":"<5-12 words>","reason":"<one short sentence>"}}"""

def judge(article, b64, mime):
    prompt = JUDGE_PROMPT.format(
        headline=article.get('headline', ''),
        subheadline=article.get('subheadline', '') or '',
        category=article.get('category', '') or '',
        caption=article.get('image_caption', '') or '(none)',
    )
    payload = {
        "model": "gpt-4o",
        "messages": [{
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}", "detail": "low"}},
            ],
        }],
        "max_tokens": 150,
        "temperature": 0,
        "response_format": {"type": "json_object"},
    }
    for attempt in range(3):
        try:
            r = session.post('https://api.openai.com/v1/chat/completions',
                             headers={'Authorization': f'Bearer {OAI}', 'Content-Type': 'application/json'},
                             data=json.dumps(payload), timeout=60)
            if r.status_code == 200:
                txt = r.json()['choices'][0]['message']['content']
                return json.loads(txt)
            if r.status_code in (429, 500, 502, 503):
                time.sleep(2 * (attempt + 1))
                continue
            return {"verdict": "ERROR", "reason": f"HTTP {r.status_code}: {r.text[:120]}"}
        except Exception as e:
            time.sleep(1.5 * (attempt + 1))
            last = str(e)
    return {"verdict": "ERROR", "reason": last if 'last' in dir() else 'unknown'}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--limit', type=int, default=60)
    ap.add_argument('--since-days', type=int, default=0)
    ap.add_argument('--json', default='')
    args = ap.parse_args()

    arts = fetch_articles(args.limit, args.since_days)
    print(f"Auditing {len(arts)} articles' hero images for mismatches...\n", flush=True)

    mismatches, errors, checked = [], [], 0
    for a in arts:
        url = a.get('image_url')
        if not url:
            continue
        b64, mime = download_image_b64(url)
        if not b64:
            errors.append((a['slug'], 'image download failed', url))
            continue
        v = judge(a, b64, mime)
        checked += 1
        verdict = (v.get('verdict') or '').upper()
        if verdict == 'MISMATCH':
            mismatches.append({
                'slug': a['slug'], 'category': a.get('category'),
                'headline': a.get('headline'),
                'photo_shows': v.get('what_photo_shows'),
                'reason': v.get('reason'), 'image_url': url,
            })
            print(f"  ✗ MISMATCH [{a.get('category')}] {a['slug'][:55]}", flush=True)
            print(f"      photo shows: {v.get('what_photo_shows')}", flush=True)
            print(f"      reason: {v.get('reason')}", flush=True)
        elif verdict == 'ERROR':
            errors.append((a['slug'], v.get('reason'), url))

    print(f"\n=== SUMMARY ===")
    print(f"Checked: {checked}   Mismatches: {len(mismatches)}   Errors: {len(errors)}")
    if errors:
        print(f"\nErrors ({len(errors)}):")
        for s, why, u in errors[:20]:
            print(f"  - {s[:55]}: {why}")
    if args.json:
        json.dump({'mismatches': mismatches, 'errors': [
            {'slug': s, 'reason': w, 'url': u} for s, w, u in errors]},
            open(args.json, 'w'), indent=2)
        print(f"\nWrote report to {args.json}")

if __name__ == '__main__':
    main()
