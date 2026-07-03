#!/usr/bin/env python3
"""render-data-cards.py — Pre-render data cards as inline HTML and inject into article body.

Reads `data_cards` and `key_takeaways` from enriched articles, builds self-contained
HTML blocks with inline styles (no external CSS), and injects them into the article
body at the right placement points. The HTML renders natively via rehypeRaw in the
React frontend — zero extra requests, zero JS overhead.

Usage:
    python3 render-data-cards.py [--limit N] [--since-hours H] [--dry-run] [--slug SLUG]
"""
import os, sys, json, re, argparse, requests
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

# ── Card HTML renderer ──────────────────────────────────────────────

def _esc(s):
    """HTML-escape text."""
    return (s or "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def render_card_html(card):
    """Render a single data card as self-contained HTML with inline styles."""
    ctype = card.get("card_type", "stat_grid")
    title = _esc(card.get("card_title", ""))
    hs = card.get("hero_stat")
    items = card.get("items", [])
    source = _esc(card.get("source_note", ""))

    # Outer container
    html = (
        '<div style="'
        'background:linear-gradient(135deg,#0B1D3A 0%,#132d54 100%);'
        'border-radius:12px;padding:24px;margin:28px 0;'
        'box-shadow:0 4px 20px rgba(11,29,58,0.3);'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;'
        'position:relative;overflow:hidden;'
        '">\n'
    )
    # Gold glow
    html += (
        '<div style="position:absolute;top:-50%;right:-20%;width:300px;height:300px;'
        'background:radial-gradient(circle,rgba(212,168,67,0.06) 0%,transparent 70%);'
        'pointer-events:none;"></div>\n'
    )

    # Title
    if title:
        html += (
            f'<div style="font-size:12px;font-weight:700;color:#D4A843;'
            f'text-transform:uppercase;letter-spacing:1.5px;'
            f'margin-bottom:16px;padding-bottom:8px;'
            f'border-bottom:1px solid rgba(212,168,67,0.2);">{title}</div>\n'
        )

    # Hero stat
    if hs:
        val = _esc(hs.get("value", ""))
        label = _esc(hs.get("label", ""))
        trend = _esc(hs.get("trend", ""))
        trend_color = "#f87171" if trend.startswith("↓") or trend.startswith("-") else "#4ade80"
        html += '<div style="display:flex;align-items:baseline;gap:10px;margin-bottom:16px;flex-wrap:wrap;">\n'
        html += f'<div style="font-size:38px;font-weight:800;color:#D4A843;line-height:1;letter-spacing:-1px;">{val}</div>\n'
        if trend:
            html += f'<div style="font-size:16px;font-weight:700;color:{trend_color};">{trend}</div>\n'
        if label:
            html += f'<div style="font-size:13px;color:rgba(255,255,255,0.6);width:100%;">{label}</div>\n'
        html += '</div>\n'

    # Body by type
    if ctype == "stat_grid":
        html += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;">\n'
        for item in items:
            v = _esc(item.get("value", ""))
            l = _esc(item.get("label", ""))
            html += (
                '<div style="background:rgba(255,255,255,0.04);border-radius:8px;'
                'padding:12px 14px;border-left:3px solid rgba(212,168,67,0.4);">\n'
                f'<div style="font-size:18px;font-weight:800;color:#fff;margin-bottom:2px;">{v}</div>\n'
                f'<div style="font-size:11px;color:rgba(255,255,255,0.45);line-height:1.3;">{l}</div>\n'
                '</div>\n'
            )
        html += '</div>\n'

    elif ctype == "comparison":
        max_nv = max((i.get("numeric_value") or 0) for i in items) or 1
        for item in items:
            name = _esc(item.get("name", ""))
            val = _esc(item.get("value", ""))
            nv = item.get("numeric_value") or 0
            pct = max(int(nv / max_nv * 100), 12)
            is_neg = nv < 0
            bar_bg = "linear-gradient(90deg,#D4A843,#e8c36a)" if not is_neg else "linear-gradient(90deg,#f87171,#ef4444)"
            html += (
                '<div style="display:flex;align-items:center;margin-bottom:6px;">\n'
                f'<div style="width:110px;text-align:right;padding-right:10px;flex-shrink:0;'
                f'font-size:11px;font-weight:600;color:rgba(255,255,255,0.7);">{name}</div>\n'
                f'<div style="flex:1;height:22px;background:rgba(255,255,255,0.05);border-radius:4px;overflow:hidden;">'
                f'<div style="height:100%;width:{pct}%;background:{bar_bg};border-radius:4px;'
                f'display:flex;align-items:center;padding-left:8px;'
                f'font-size:11px;font-weight:700;color:#0B1D3A;min-width:50px;">{val}</div>'
                f'</div>\n</div>\n'
            )

    elif ctype == "timeline":
        html += (
            '<div style="margin:8px 0;border-left:2px solid rgba(212,168,67,0.3);padding-left:16px;">\n'
        )
        for item in items:
            dt = _esc(item.get("date", ""))
            ev = _esc(item.get("event", ""))
            html += (
                '<div style="margin-bottom:12px;position:relative;">\n'
                '<div style="position:absolute;left:-21px;top:6px;width:10px;height:10px;'
                'border-radius:50%;background:#D4A843;"></div>\n'
                f'<div style="font-size:11px;font-weight:700;color:#D4A843;margin-bottom:2px;">{dt}</div>\n'
                f'<div style="font-size:12px;color:rgba(255,255,255,0.65);line-height:1.4;">{ev}</div>\n'
                '</div>\n'
            )
        html += '</div>\n'

    elif ctype == "highlights":
        for item in items:
            stat = _esc(item.get("stat", ""))
            text = _esc(item.get("text", ""))
            stat_html = (
                f'<span style="display:inline-block;background:rgba(212,168,67,0.15);'
                f'color:#D4A843;font-weight:700;font-size:11px;padding:1px 6px;'
                f'border-radius:3px;margin-right:4px;">{stat}</span> '
            ) if stat else ""
            html += (
                f'<div style="font-size:12px;color:rgba(255,255,255,0.6);'
                f'padding:5px 0 5px 16px;position:relative;line-height:1.4;">'
                f'<span style="position:absolute;left:3px;color:#D4A843;font-weight:700;">›</span>'
                f'{stat_html}{text}</div>\n'
            )

    # Source note
    if source:
        html += (
            f'<div style="font-size:10px;color:rgba(255,255,255,0.25);margin-top:10px;'
            f'padding-top:8px;border-top:1px solid rgba(255,255,255,0.06);">{source}</div>\n'
        )

    html += '</div>\n'
    return html


def render_takeaways_html(takeaways):
    """Render key takeaways as a styled HTML block."""
    if not takeaways:
        return ""
    html = (
        '<div style="background:#f9fafb;border-radius:10px;padding:16px 20px;'
        'margin:24px 0;border-left:3px solid #D4A843;'
        'font-family:-apple-system,BlinkMacSystemFont,\'Segoe UI\',sans-serif;">\n'
        '<div style="font-size:12px;text-transform:uppercase;letter-spacing:1px;'
        'color:#999;margin:0 0 10px;font-weight:700;">Key Takeaways</div>\n<ul style="margin:0;padding:0 0 0 16px;">\n'
    )
    for t in takeaways:
        html += f'<li style="font-size:13px;color:#333;line-height:1.5;margin-bottom:4px;">{_esc(t)}</li>\n'
    html += '</ul>\n</div>\n'
    return html


# ── Body injection ──────────────────────────────────────────────────

def inject_cards_into_body(body, data_cards, key_takeaways):
    """Inject rendered card HTML into article body at appropriate positions."""
    if not data_cards and not key_takeaways:
        return body

    # Split body into paragraphs
    paras = re.split(r'(\n\n+)', body)  # Keep delimiters

    # Count actual content paragraphs (not delimiters)
    content_indices = [i for i, p in enumerate(paras) if p.strip() and not re.match(r'^\n+$', p)]
    n_content = len(content_indices)

    # Placement map: group cards by placement_hint
    after_lead = []
    mid_article = []
    before_conclusion = []

    for card in (data_cards or []):
        hint = card.get("placement_hint", "mid_article")
        rendered = render_card_html(card)
        if hint == "after_lead":
            after_lead.append(rendered)
        elif hint == "before_conclusion":
            before_conclusion.append(rendered)
        else:
            mid_article.append(rendered)

    # Render takeaways
    takeaways_html = render_takeaways_html(key_takeaways)

    # Determine insertion points (as indices into paras list)
    # after_lead → after 2nd content paragraph
    # mid_article → after ~60% of content
    # before_conclusion → before last 2 content paragraphs

    insertions = {}  # para_index -> list of HTML strings to insert after

    if takeaways_html or after_lead:
        # Insert after 2nd paragraph (or 1st if only 1-2 paras)
        idx = content_indices[min(1, n_content - 1)] if n_content > 0 else 0
        insertions.setdefault(idx, [])
        if takeaways_html:
            insertions[idx].append(takeaways_html)
        insertions[idx].extend(after_lead)

    if mid_article:
        mid_pos = int(n_content * 0.6)
        mid_pos = max(mid_pos, 3)  # At least after 3rd paragraph
        mid_pos = min(mid_pos, n_content - 2)  # Leave room before end
        idx = content_indices[mid_pos] if mid_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(mid_article)

    if before_conclusion:
        conc_pos = max(n_content - 3, int(n_content * 0.8))
        conc_pos = min(conc_pos, n_content - 1)
        # Don't overlap with mid_article
        idx = content_indices[conc_pos] if conc_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(before_conclusion)

    # Rebuild body with insertions
    result = []
    for i, part in enumerate(paras):
        result.append(part)
        if i in insertions:
            result.append("\n\n")
            result.append("\n".join(insertions[i]))

    return "".join(result)


# ── Main ────────────────────────────────────────────────────────────

def fetch_articles(limit, since_hours, slug=None):
    """Fetch enriched articles that haven't had cards injected yet."""
    params = {
        "select": "id,slug,headline,body,data_cards,key_takeaways,enriched_at",
        "enriched_at": "not.is.null",
        "order": "published_at.desc",
        "limit": str(limit),
    }
    if slug:
        params["slug"] = f"eq.{slug}"
    else:
        since = (datetime.now(timezone.utc) - timedelta(hours=since_hours)).isoformat()
        params["published_at"] = f"gte.{since}"

    r = requests.get(
        f"{SUPABASE_URL}/rest/v1/p2_articles",
        headers=HEADERS, params=params
    )
    r.raise_for_status()
    return r.json()


def patch_body(article_id, new_body):
    """Update article body in Supabase."""
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={**HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json={"body": new_body, "cards_rendered_at": datetime.now(timezone.utc).isoformat()}
    )
    r.raise_for_status()


# Marker to detect if cards are already injected
CARD_MARKER = '<!-- data-card -->'

def has_cards_already(body):
    return CARD_MARKER in body


def render_card_html_wrapped(card):
    """Render card with detection marker."""
    return f'{CARD_MARKER}\n{render_card_html(card)}'


def inject_cards_into_body_marked(body, data_cards, key_takeaways):
    """Same as inject_cards_into_body but adds markers for idempotency."""
    if not data_cards and not key_takeaways:
        return body

    paras = re.split(r'(\n\n+)', body)
    content_indices = [i for i, p in enumerate(paras) if p.strip() and not re.match(r'^\n+$', p)]
    n_content = len(content_indices)
    if n_content == 0:
        return body

    after_lead = []
    mid_article = []
    before_conclusion = []

    for card in (data_cards or []):
        hint = card.get("placement_hint", "mid_article")
        rendered = f'{CARD_MARKER}\n{render_card_html(card)}'
        if hint == "after_lead":
            after_lead.append(rendered)
        elif hint == "before_conclusion":
            before_conclusion.append(rendered)
        else:
            mid_article.append(rendered)

    takeaways_html = ""
    if key_takeaways:
        takeaways_html = f'{CARD_MARKER}\n{render_takeaways_html(key_takeaways)}'

    insertions = {}

    if takeaways_html or after_lead:
        idx = content_indices[min(1, n_content - 1)]
        insertions.setdefault(idx, [])
        if takeaways_html:
            insertions[idx].append(takeaways_html)
        insertions[idx].extend(after_lead)

    if mid_article:
        mid_pos = max(int(n_content * 0.6), 3)
        mid_pos = min(mid_pos, n_content - 2)
        if mid_pos < 0:
            mid_pos = n_content - 1
        idx = content_indices[mid_pos] if mid_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(mid_article)

    if before_conclusion:
        conc_pos = max(n_content - 3, int(n_content * 0.8))
        conc_pos = min(conc_pos, n_content - 1)
        idx = content_indices[conc_pos] if conc_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(before_conclusion)

    result = []
    for i, part in enumerate(paras):
        result.append(part)
        if i in insertions:
            result.append("\n\n")
            result.append("\n\n".join(insertions[i]))

    return "".join(result)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--since-hours", type=int, default=6)
    ap.add_argument("--slug", help="Process a specific article by slug")
    ap.add_argument("--dry-run", action="store_true", help="Don't write to DB")
    ap.add_argument("--force", action="store_true", help="Re-render even if already injected")
    args = ap.parse_args()

    articles = fetch_articles(args.limit, args.since_hours, args.slug)
    print(f"📊 Found {len(articles)} enriched articles")

    rendered = 0
    skipped = 0
    errors = 0

    for art in articles:
        slug = art["slug"]
        body = art.get("body") or ""
        data_cards = art.get("data_cards") or []
        key_takeaways = art.get("key_takeaways") or []

        if not data_cards and not key_takeaways:
            skipped += 1
            continue

        if has_cards_already(body) and not args.force:
            skipped += 1
            continue

        # Strip old cards if --force re-render
        if args.force and has_cards_already(body):
            # Remove old card blocks: from marker to closing </div>
            body = re.sub(
                r'<!-- data-card -->\n<div style="background:#f9fafb.*?</div>\n',
                '', body, flags=re.DOTALL
            )
            body = re.sub(
                r'<!-- data-card -->\n<div style="background:linear-gradient.*?</div>\n</div>\n',
                '', body, flags=re.DOTALL
            )

        try:
            new_body = inject_cards_into_body_marked(body, data_cards, key_takeaways)
            if new_body == body:
                skipped += 1
                continue

            if args.dry_run:
                print(f"  ✅ [DRY] {slug} — {len(data_cards)} cards + {len(key_takeaways)} takeaways")
                # Show a snippet
                idx = new_body.find(CARD_MARKER)
                if idx >= 0:
                    print(f"     Preview: ...{new_body[idx:idx+200]}...")
            else:
                patch_body(art["id"], new_body)
                print(f"  ✅ {slug} — {len(data_cards)} cards + {len(key_takeaways)} takeaways injected")
            rendered += 1
        except Exception as e:
            print(f"  ❌ {slug}: {e}", file=sys.stderr)
            errors += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done: {rendered} rendered, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
