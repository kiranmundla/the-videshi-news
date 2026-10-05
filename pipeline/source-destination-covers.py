#!/usr/bin/env python3
"""One-time: source cover images for all 49 travel destinations via Pexels.

Writes public/images/destinations/<key>.jpg + a manifest with photographer credit.
Run: python3 -u source-destination-covers.py
"""
import json, os, subprocess, sys, time

REPO = os.path.expanduser("~/workspace/the-videshi-news")
OUT = os.path.join(REPO, "public", "images", "destinations")
os.makedirs(OUT, exist_ok=True)

def load_env(path):
    with open(os.path.expanduser(path)) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k, v)

load_env("~/workspace/.env.pexels")
KEY = os.environ.get("PEXELS_API_KEY")
if not KEY:
    sys.exit("PEXELS_API_KEY missing")

QUERIES = {
    "rajasthan": "Rajasthan palace India",
    "kerala": "Kerala backwaters houseboat",
    "goa": "Goa beach palm",
    "himachal-pradesh": "Himachal Pradesh Himalaya mountains",
    "uttarakhand": "Uttarakhand Himalayas temple",
    "kashmir": "Kashmir Dal Lake houseboat",
    "tamil-nadu": "Tamil Nadu Meenakshi temple",
    "karnataka": "Hampi ruins Karnataka",
    "northeast-india": "Meghalaya living root bridge",
    "bali": "Bali temple rice terrace",
    "thailand": "Thailand Phi Phi island beach",
    "vietnam": "Ha Long Bay Vietnam",
    "sri-lanka": "Sri Lanka Sigiriya",
    "maldives": "Maldives overwater villa",
    "singapore": "Singapore Marina Bay Sands",
    "japan": "Japan Kyoto cherry blossom temple",
    "cancun": "Cancun beach turquoise",
    "cabo": "Cabo San Lucas arch",
    "riviera-maya": "Tulum Mexico beach ruins",
    "puerto-vallarta": "Puerto Vallarta malecon",
    "jamaica": "Jamaica beach",
    "dominican-republic": "Dominican Republic Punta Cana beach",
    "bahamas": "Bahamas Exuma beach",
    "aruba": "Aruba beach palm",
    "london": "London Big Ben",
    "switzerland": "Swiss Alps Matterhorn",
    "italy": "Amalfi Coast Positano Italy",
    "france": "Paris Eiffel Tower",
    "spain": "Barcelona Sagrada Familia Spain",
    "greece": "Santorini Greece white",
    "iceland": "Iceland waterfall northern lights",
    "portugal": "Lisbon Portugal tram",
    "scandinavia": "Norway fjord Geiranger",
    "hawaii": "Hawaii Waikiki beach",
    "national-parks": "Yellowstone Grand Prismatic",
    "new-york-city": "New York City Manhattan skyline",
    "florida": "Florida Miami beach",
    "alaska": "Alaska glacier",
    "banff": "Banff Lake Louise Canada",
    "dubai": "Dubai skyline Burj Khalifa",
    "abu-dhabi": "Abu Dhabi Sheikh Zayed Grand Mosque",
    "oman": "Oman Muscat",
    "south-africa": "Cape Town Table Mountain",
    "kenya": "Kenya Masai Mara safari elephant",
    "egypt": "Egypt Giza pyramids",
    "morocco": "Morocco Marrakech medina",
    "new-zealand": "New Zealand Milford Sound",
    "australia": "Sydney Opera House harbour",
    "fiji": "Fiji tropical island",
}

def curl_json(url, params=None):
    cmd = ["curl", "-sS", "-m", "30", "-H", f"Authorization: {KEY}", "-G", url]
    for k, v in (params or {}).items():
        cmd += ["--data-urlencode", f"{k}={v}"]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=40)
    return json.loads(r.stdout or "{}")

manifest = {}
for i, (key, q) in enumerate(QUERIES.items()):
    dest = os.path.join(OUT, f"{key}.jpg")
    if os.path.exists(dest) and os.path.getsize(dest) > 10000:
        print(f"[{i+1}/49] {key}: cached, skip")
        continue
    try:
        data = curl_json("https://api.pexels.com/v1/search",
                         {"query": q, "orientation": "landscape",
                          "size": "medium", "per_page": 5})
        photos = data.get("photos", [])
        if not photos:
            print(f"[{i+1}/49] {key}: NO RESULTS for '{q}'")
            continue
        p = photos[0]
        img_url = p["src"]["large"]
        r = subprocess.run(["curl", "-sS", "-m", "60", "-o", dest, img_url],
                           capture_output=True, timeout=70)
        size = os.path.getsize(dest) if os.path.exists(dest) else 0
        manifest[key] = {
            "query": q,
            "photographer": p.get("photographer"),
            "photographer_url": p.get("photographer_url"),
            "pexels_url": p.get("url"),
            "bytes": size,
        }
        print(f"[{i+1}/49] {key}: ok ({size//1024}KB) by {p.get('photographer')}")
    except Exception as e:
        print(f"[{i+1}/49] {key}: ERROR {e}")
    time.sleep(0.4)  # stay well under rate limits

with open(os.path.join(OUT, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)
print(f"done. {len(manifest)} in manifest.")
