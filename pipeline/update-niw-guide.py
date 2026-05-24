import json, os, urllib.request

# Load env
for line in open(os.path.expanduser('~/.env.supabase')):
    line = line.strip()
    if line and not line.startswith('#') and '=' in line:
        k, v = line.split('=', 1)
        os.environ[k] = v

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

content = open("niw-guide-content.md").read()

data = {
    "title": "EB-2 NIW: The Complete National Interest Waiver Guide for Indians",
    "subtitle": "Skip PERM, self-petition, and take control of your green card journey",
    "content": content,
    "meta_description": "Complete EB-2 NIW guide for Indian professionals: Dhanasar framework, evidence strategies, expert letters, dual-track with PERM, costs, and common mistakes.",
    "reading_time_min": 25,
    "last_updated": "2026-05-24T00:00:00Z",
}

req = urllib.request.Request(
    f"{SUPABASE_URL}/rest/v1/immigration_guides?slug=eq.national-interest-waiver",
    data=json.dumps(data).encode(),
    headers={
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal"
    },
    method="PATCH"
)
try:
    resp = urllib.request.urlopen(req)
    print(f"Updated NIW guide: {resp.status} — {len(content)} chars, ~25 min read")
except Exception as e:
    print(f"Error: {e}")
    if hasattr(e, 'read'):
        print(e.read().decode())
