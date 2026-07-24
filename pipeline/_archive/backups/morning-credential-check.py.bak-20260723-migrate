#!/usr/bin/env python3
"""
Morning credential / billing pre-flight check for The Videshi.

Probes every service the daily distribution + generation pipeline depends on,
and reports which are HEALTHY vs DEAD (and why) BEFORE the day's runs fire.

Design notes / gotchas (see ~/AGENTS.md):
  - X: free endpoints (users/me) do NOT reveal credit depletion. We probe a
    metered read endpoint and treat HTTP 402 CreditsDepleted as DEAD-billing,
    distinct from auth failure (401/403).
  - YouTube / Google APIs: httplib2 ignores the egress proxy -> must use
    requests for the token refresh (curl/requests honor proxy env).
  - OpenAI: distinguish 429 insufficient_quota (billing) from a real auth error.
  - Output is a compact status block; exit code 0 always (report-only).
"""
import os, sys, json, subprocess, urllib.parse

PIPELINE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.expanduser("~/workspace")

def load_env(path):
    d = {}
    p = os.path.join(WS, path) if not os.path.isabs(path) else path
    try:
        with open(p) as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                k, v = line.split("=", 1)
                d[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return d

results = []  # (service, status, detail)  status in HEALTHY/DEAD/WARN

# ---------------- X / Twitter ----------------
def check_x():
    env = load_env(".env.twitter")
    try:
        from requests_oauthlib import OAuth1Session
    except Exception as e:
        return ("X (Twitter)", "WARN", f"lib missing: {e}")
    try:
        oauth = OAuth1Session(
            env.get("TWITTER_CONSUMER_KEY"), env.get("TWITTER_CONSUMER_SECRET"),
            env.get("TWITTER_ACCESS_TOKEN"), env.get("TWITTER_ACCESS_TOKEN_SECRET"),
        )
        # free endpoint -> proves auth + identity
        me = oauth.get("https://api.twitter.com/2/users/me", timeout=30)
        if me.status_code in (401, 403):
            return ("X (Twitter)", "DEAD", f"auth failed {me.status_code}")
        if me.status_code != 200:
            return ("X (Twitter)", "WARN", f"users/me {me.status_code}")
        uid = me.json().get("data", {}).get("id")
        # metered endpoint -> reveals credit depletion (402)
        r = oauth.get(f"https://api.twitter.com/2/users/{uid}/tweets",
                      params={"max_results": 5}, timeout=30)
        if r.status_code == 402:
            return ("X (Twitter)", "DEAD", "402 CreditsDepleted (metered reads)")
        if r.status_code == 429:
            return ("X (Twitter)", "WARN", "429 rate-limited (transient)")
        if r.status_code == 200:
            return ("X (Twitter)", "HEALTHY", "auth + credits OK")
        return ("X (Twitter)", "WARN", f"tweets read {r.status_code}")
    except Exception as e:
        return ("X (Twitter)", "WARN", f"probe error: {e}")

# ---------------- YouTube ----------------
def check_youtube():
    env = load_env(".env.youtube")
    try:
        import requests
        r = requests.post("https://oauth2.googleapis.com/token", data={
            "client_id": env.get("YOUTUBE_CLIENT_ID"),
            "client_secret": env.get("YOUTUBE_CLIENT_SECRET"),
            "refresh_token": env.get("YOUTUBE_REFRESH_TOKEN"),
            "grant_type": "refresh_token",
        }, timeout=30)
        if r.status_code == 200 and r.json().get("access_token"):
            tok = r.json()["access_token"]
            # confirm channel reachable
            ch = requests.get("https://www.googleapis.com/youtube/v3/channels",
                              params={"part": "id", "mine": "true"},
                              headers={"Authorization": f"Bearer {tok}"}, timeout=30)
            if ch.status_code == 200:
                return ("YouTube", "HEALTHY", "token refresh + channel OK")
            return ("YouTube", "WARN", f"channel list {ch.status_code}")
        return ("YouTube", "DEAD", f"token refresh {r.status_code}: {r.text[:120]}")
    except Exception as e:
        return ("YouTube", "WARN", f"probe error: {e}")

# ---------------- Instagram ----------------
def check_instagram():
    env = load_env(".env.instagram")
    try:
        import requests
        uid = env.get("INSTAGRAM_USER_ID")
        tok = env.get("INSTAGRAM_ACCESS_TOKEN")
        r = requests.get(f"https://graph.facebook.com/v21.0/{uid}",
                         params={"fields": "username", "access_token": tok}, timeout=30)
        if r.status_code == 200 and "username" in r.json():
            return ("Instagram", "HEALTHY", f"@{r.json()['username']}")
        err = r.json().get("error", {})
        return ("Instagram", "DEAD", f"{err.get('code')}: {err.get('message','?')[:90]}")
    except Exception as e:
        return ("Instagram", "WARN", f"probe error: {e}")

# ---------------- Threads ----------------
def check_threads():
    env = load_env(".env.threads")
    try:
        import requests
        tok = env.get("THREADS_ACCESS_TOKEN")
        r = requests.get("https://graph.threads.net/v1.0/me",
                         params={"fields": "username", "access_token": tok}, timeout=30)
        if r.status_code == 200 and "username" in r.json():
            return ("Threads", "HEALTHY", f"@{r.json()['username']}")
        err = r.json().get("error", {})
        return ("Threads", "DEAD", f"{err.get('code')}: {err.get('message','?')[:90]}")
    except Exception as e:
        return ("Threads", "WARN", f"probe error: {e}")

# ---------------- OpenAI ----------------
def check_openai():
    env = load_env(".env.openai")
    try:
        import requests
        r = requests.get("https://api.openai.com/v1/models",
                         headers={"Authorization": f"Bearer {env.get('OPENAI_API_KEY')}"}, timeout=30)
        if r.status_code == 401:
            return ("OpenAI", "DEAD", "401 invalid key")
        if r.status_code != 200:
            return ("OpenAI", "WARN", f"models list {r.status_code}")
        # tiny metered completion to surface quota/billing limits
        c = requests.post("https://api.openai.com/v1/chat/completions",
                          headers={"Authorization": f"Bearer {env.get('OPENAI_API_KEY')}",
                                   "Content-Type": "application/json"},
                          data=json.dumps({"model": "gpt-4o-mini",
                                           "messages": [{"role": "user", "content": "ok"}],
                                           "max_tokens": 1}), timeout=30)
        if c.status_code == 200:
            return ("OpenAI", "HEALTHY", "auth + quota OK")
        if c.status_code == 429:
            return ("OpenAI", "DEAD", "429 insufficient_quota (billing)")
        body = ""
        try:
            body = c.json().get("error", {}).get("code") or c.text[:90]
        except Exception:
            body = c.text[:90]
        return ("OpenAI", "DEAD", f"{c.status_code}: {body}")
    except Exception as e:
        return ("OpenAI", "WARN", f"probe error: {e}")

# ---------------- Shotstack ----------------
def check_shotstack():
    env = load_env(os.path.join(PIPELINE, ".env.shotstack"))
    try:
        import requests
        key = env.get("SHOTSTACK_PRODUCTION_KEY")
        # render-status of a bogus id: 401/403 = bad key; 4xx-not-auth = key OK
        r = requests.get("https://api.shotstack.io/edit/v1/render/00000000-0000-0000-0000-000000000000",
                         headers={"x-api-key": key}, timeout=30)
        if r.status_code in (401, 403):
            return ("Shotstack", "DEAD", f"auth {r.status_code}")
        return ("Shotstack", "HEALTHY", "key accepted")
    except Exception as e:
        return ("Shotstack", "WARN", f"probe error: {e}")

CHECKS = [check_x, check_youtube, check_instagram, check_threads, check_openai, check_shotstack]

def main():
    for fn in CHECKS:
        try:
            results.append(fn())
        except Exception as e:
            results.append((fn.__name__, "WARN", f"crash: {e}"))

    icon = {"HEALTHY": "✅", "DEAD": "❌", "WARN": "⚠️"}
    dead = [r for r in results if r[1] == "DEAD"]
    warn = [r for r in results if r[1] == "WARN"]

    lines = []
    for svc, st, detail in results:
        lines.append(f"{icon.get(st,'?')} {svc}: {detail}")
    report = "\n".join(lines)

    summary = {
        "dead": [r[0] for r in dead],
        "warn": [r[0] for r in warn],
        "healthy": [r[0] for r in results if r[1] == "HEALTHY"],
    }
    print(report)
    print("\n__SUMMARY__ " + json.dumps(summary))

if __name__ == "__main__":
    main()
