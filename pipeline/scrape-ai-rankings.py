#!/usr/bin/env python3
"""
Scrape AI model rankings from the official Chatbot Arena (LMSYS/LMArena)
leaderboard dataset on HuggingFace.

Writes: public/data/ai-rankings.json
Source: https://huggingface.co/datasets/lmarena-ai/leaderboard-dataset

Usage:
    python3 pipeline/scrape-ai-rankings.py          # default top 10
    python3 pipeline/scrape-ai-rankings.py --top 15  # top 15
"""

import json, os, sys, re, subprocess, argparse
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(REPO, "public", "data", "ai-rankings.json")
HF_API = "https://datasets-server.huggingface.co/rows"
DATASET = "lmarena-ai/leaderboard-dataset"
CONFIG = "text_style_control"
SPLIT = "latest"

# ── Clean model names ──────────────────────────────────────────────
def clean_model_name(raw: str) -> str:
    """Turn 'claude-opus-4-6-thinking' into 'Claude Opus 4.6 (Thinking)'."""
    name = raw.strip()

    # Handle -thinking suffix
    thinking = False
    if name.endswith("-thinking"):
        thinking = True
        name = name[:-9]

    # Replace version-like patterns: e.g. 4-6 → 4.6, 3-1 → 3.1, 5.6 stays
    # Only replace single-digit-dash-single-digit that look like versions
    name = re.sub(r'(\d)-(\d)(?!\d)', r'\1.\2', name)

    # Title-case, keeping dots
    parts = name.split("-")
    cleaned = []
    for p in parts:
        if re.match(r'^\d', p):
            cleaned.append(p)
        else:
            cleaned.append(p.capitalize())
    name = " ".join(cleaned)

    if thinking:
        name += " (Thinking)"

    # Clean up known patterns
    name = name.replace("Gpt", "GPT")
    name = name.replace("Sol Xhigh", "Sol (xHigh)")
    name = name.replace("Sol High", "Sol (High)")
    name = name.replace(" High", " (High)").replace(" (High)", " (High)")
    # Fix double parens
    name = re.sub(r'\((\w+)\)\s*\((\w+)\)', r'(\1, \2)', name)

    return name


# ── Organization display names ────────────────────────────────────
ORG_DISPLAY = {
    "anthropic": "Anthropic",
    "openai": "OpenAI",
    "google": "Google",
    "meta": "Meta",
    "moonshot": "Moonshot AI",
    "deepseek": "DeepSeek",
    "alibaba": "Alibaba",
    "mistral": "Mistral AI",
    "xai": "xAI",
    "cohere": "Cohere",
    "zhipu": "Zhipu AI",
    "01-ai": "01.AI",
    "microsoft": "Microsoft",
    "amazon": "Amazon",
    "nvidia": "NVIDIA",
    "apple": "Apple",
    "tencent": "Tencent",
    "baidu": "Baidu",
    "bytedance": "ByteDance",
    "reka": "Reka AI",
    "ai21": "AI21 Labs",
    "perplexity": "Perplexity",
}

# Companies with prominent Indian-origin leadership
INDIAN_LEADERSHIP = {
    "google": "Sundar Pichai, CEO",
    "microsoft": "Satya Nadella, CEO",
    "nvidia": "Indian engineering leadership",
}


def fetch_rankings(top_n: int = 10) -> list:
    """Fetch latest overall rankings from HuggingFace datasets API."""
    url = f"{HF_API}?dataset={DATASET}&config={CONFIG}&split={SPLIT}&offset=0&length=100"
    result = subprocess.run(
        ["curl", "-sS", url],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        print(f"ERROR: curl failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(result.stdout)
    if "rows" not in data:
        print(f"ERROR: No rows in response: {json.dumps(data)[:300]}", file=sys.stderr)
        sys.exit(1)

    rows = [r["row"] for r in data["rows"]]
    overall = [r for r in rows if r.get("category") == "overall"]
    overall.sort(key=lambda x: x.get("rank", 999))
    return overall[:top_n]


def load_previous() -> dict:
    """Load previous rankings for change detection."""
    if not os.path.exists(OUT_PATH):
        return {}
    try:
        with open(OUT_PATH) as f:
            prev = json.load(f)
        # Build model_name → rank mapping from previous
        return {m["model_key"]: m["rank"] for m in prev.get("models", [])}
    except Exception:
        return {}


def build_output(rankings: list, prev_ranks: dict) -> dict:
    """Build the output JSON structure."""
    models = []
    publish_date = rankings[0].get("leaderboard_publish_date", "") if rankings else ""

    for r in rankings:
        model_key = r["model_name"]
        rank = r["rank"]
        org_key = (r.get("organization") or "unknown").lower()
        company = ORG_DISPLAY.get(org_key, org_key.title())

        # Compute rank change (positive = moved up)
        prev_rank = prev_ranks.get(model_key)
        change = (prev_rank - rank) if prev_rank is not None else None

        entry = {
            "rank": rank,
            "model": clean_model_name(model_key),
            "model_key": model_key,
            "company": company,
            "org_key": org_key,
            "rating": round(r.get("rating", 0)),
            "votes": int(r.get("vote_count", 0)),
            "change": change,
            "license": r.get("license", "Unknown"),
        }

        # Add Indian leadership note if applicable
        if org_key in INDIAN_LEADERSHIP:
            entry["indian_leader"] = INDIAN_LEADERSHIP[org_key]

        models.append(entry)

    return {
        "updated_at": publish_date or datetime.utcnow().strftime("%Y-%m-%d"),
        "fetched_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Chatbot Arena (lmarena.ai)",
        "source_url": "https://lmarena.ai/leaderboard",
        "methodology": "Bradley-Terry ratings from crowdsourced blind comparisons",
        "models": models,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top", type=int, default=10, help="Number of top models")
    args = parser.parse_args()

    print(f"Fetching top {args.top} AI model rankings from Chatbot Arena...")
    rankings = fetch_rankings(args.top)
    if not rankings:
        print("ERROR: No rankings returned", file=sys.stderr)
        sys.exit(1)

    print(f"  Got {len(rankings)} models, #1: {rankings[0]['model_name']}")

    prev_ranks = load_previous()
    output = build_output(rankings, prev_ranks)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w") as f:
        json.dump(output, f, indent=2)

    print(f"  Wrote {OUT_PATH}")
    print(f"  Published: {output['updated_at']}")
    for m in output["models"]:
        ch = ""
        if m["change"] is not None:
            if m["change"] > 0: ch = f" ▲{m['change']}"
            elif m["change"] < 0: ch = f" ▼{abs(m['change'])}"
            else: ch = " —"
        print(f"    #{m['rank']}: {m['model']} ({m['company']}) — {m['rating']}{ch}")


if __name__ == "__main__":
    main()
