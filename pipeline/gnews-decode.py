#!/usr/bin/env python3
"""Decode Google News /rss/articles/ URLs to real publisher URLs using curl.

Mirrors googlenewsdecoder's batchexecute flow but uses curl (Python requests/urllib
fail through this box's proxy). Usage:
    python3 gnews-decode.py < url_list.txt
    python3 gnews-decode.py "https://news.google.com/rss/articles/...."
Prints: <article_id>\t<decoded_url> (or ERROR).
"""
import json, re, subprocess, sys
from urllib.parse import urlparse, quote, unquote

GARTURLREQ_CTX = [
    ["X", "X", ["X", "X"], None, None, 1, 1, "US:en", None, 1, None, None, None, None, None, 0, 1],
    "X", "X", 1, [1, 1, 1], 1, 1, None, 0, 0, None, 0,
]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"

def run_curl(args, data=None):
    r = subprocess.run(["curl", "-sS", "--max-time", "30", "-A", UA] + args,
                       input=data, capture_output=True, text=True, timeout=60)
    return r.stdout

def fetch_sig(art_id):
    url = f"https://news.google.com/rss/articles/{art_id}?hl=en-US&gl=US&ceid=US%3Aen"
    # manual redirect following, only within news.google.com
    current = url
    for _ in range(4):
        out = run_curl(["-D", "-", "-o", "/tmp/gnews_page.html", current])
        head, _, _ = out.partition("\r\n\r\n")
        loc = None
        for line in head.splitlines():
            if line.lower().startswith("location:"):
                loc = line.split(":", 1)[1].strip()
        if loc and urlparse(loc).hostname in (None, "news.google.com"):
            current = loc if loc.startswith("http") else "https://news.google.com" + loc
            continue
        break
    html = open("/tmp/gnews_page.html", encoding="utf-8", errors="replace").read()
    sg = re.search(r'data-n-a-sg="([^"]+)"', html)
    ts = re.search(r'data-n-a-ts="([^"]+)"', html)
    if sg and ts:
        return sg.group(1), ts.group(1)
    return None

def build_body(items):
    envelopes = []
    for req_id, art_id, ts, sig in items:
        inner = ["garturlreq", GARTURLREQ_CTX, art_id,
                 int(ts) if str(ts).isdigit() else ts, sig]
        envelopes.append(["Fbv4je", json.dumps(inner, separators=(",", ":")), None, str(req_id)])
    return "f.req=" + quote(json.dumps([envelopes], separators=(",", ":")), safe="")

def parse_response(text):
    body = text
    if "\n\n" in body:
        body = body.split("\n\n", 1)[1]
    body = body.lstrip()
    if body.startswith(")]}'"):
        body = body.split("\n", 1)[1] if "\n" in body else body[4:]
        body = body.lstrip()
    rows = json.loads(body)
    if rows and rows[-1] and isinstance(rows[-1], list) and rows[-1][0] == "di":
        rows = rows[:-1]
    if rows and isinstance(rows[-1], list) and rows[-1] and rows[-1][0] == "e":
        rows = rows[:-1]
    pairs = []
    for row in rows:
        if not (isinstance(row, list) and len(row) >= 3):
            continue
        payload = row[2]
        if row[0] == "wrb.fr" or row[1] == "Fbv4je":
            if isinstance(payload, str):
                payload = json.loads(payload)
            if isinstance(payload, list) and payload and payload[0] == "garturlres":
                req_id = None
                for cell in reversed(row[3:]):
                    if cell is not None:
                        req_id = str(cell)
                        break
                pairs.append((req_id, payload[1]))
    return pairs

def art_id(url):
    u = urlparse(url)
    path = u.path.split("/")
    if u.hostname == "news.google.com" and len(path) > 1 and path[-2] in ("articles", "read"):
        return path[-1] or None
    return None

def main():
    urls = []
    if len(sys.argv) > 1:
        urls = sys.argv[1:]
    else:
        urls = [l.strip() for l in sys.stdin if l.strip()]
    items, idmap, errors = [], {}, {}
    for i, u in enumerate(urls):
        aid = art_id(u)
        if not aid:
            print(f"SKIP\t{u}")
            continue
        sig = fetch_sig(aid)
        if not sig:
            errors[i] = u
            continue
        ts, s = sig[1], sig[0]
        items.append((i, aid, ts, s))
        idmap[i] = u
    results = {}
    if items:
        body = build_body(items)
        out = run_curl(["-X", "POST", "--data-binary", "@-",
                        "-H", "Content-Type: application/x-www-form-urlencoded;charset=UTF-8",
                        "https://news.google.com/_/DotsSplashUi/data/batchexecute"],
                       data=body)
        try:
            for req_id, durl in parse_response(out):
                results[int(req_id)] = durl
        except Exception as e:
            print(f"BATCHEXECUTE_ERROR\t{e}\t{out[:200]}", file=sys.stderr)
    for i, u in enumerate(urls):
        aid = art_id(u)
        if not aid:
            continue
        if i in results:
            print(f"{aid}\t{results[i]}")
        else:
            print(f"{aid}\tERROR")

if __name__ == "__main__":
    main()
