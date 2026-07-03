#!/usr/bin/env python3
"""render-data-cards.py — Pre-render data cards as inline HTML and inject into article body.

Uses CSS class names (defined in index.css as .vdc-*) instead of inline styles,
because React/rehype-raw strips style="" string attributes.

Usage:
    python3 render-data-cards.py [--limit N] [--since-hours H] [--dry-run] [--slug SLUG] [--force]
"""
import os, sys, json, re, argparse, requests
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

CARD_MARKER = '<!-- data-card -->'

def _esc(s):
    return (str(s) if s is not None else "").replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")


def render_card_html(card):
    ctype = card.get("card_type", "stat_grid")
    title = _esc(card.get("card_title", ""))
    hs = card.get("hero_stat")
    items = card.get("items", [])
    source = _esc(card.get("source_note", ""))

    html = '<div class="vdc">\n<div class="vdc-glow"></div>\n'

    if title:
        html += f'<div class="vdc-title">{title}</div>\n'

    if hs:
        val = _esc(hs.get("value", ""))
        label = _esc(hs.get("label", ""))
        trend = _esc(hs.get("trend", ""))
        trend_cls = "vdc-hero-trend-neg" if (trend.startswith("↓") or trend.startswith("-")) else "vdc-hero-trend"
        html += '<div class="vdc-hero">\n'
        html += f'<div class="vdc-hero-num">{val}</div>\n'
        if trend:
            html += f'<div class="{trend_cls}">{trend}</div>\n'
        if label:
            html += f'<div class="vdc-hero-label">{label}</div>\n'
        html += '</div>\n'

    if ctype == "stat_grid":
        html += '<div class="vdc-grid">\n'
        for item in items:
            v = _esc(item.get("value", ""))
            l = _esc(item.get("label", ""))
            html += f'<div class="vdc-stat"><div class="vdc-stat-val">{v}</div><div class="vdc-stat-lbl">{l}</div></div>\n'
        html += '</div>\n'

    elif ctype == "comparison":
        max_nv = max((abs(i.get("numeric_value") or 0) for i in items), default=1) or 1
        for item in items:
            name = _esc(item.get("name", item.get("label", "")))
            val = _esc(item.get("value", ""))
            nv = item.get("numeric_value") or 0
            pct = max(int(abs(nv) / abs(max_nv) * 100), 12)
            is_neg = nv < 0
            fill_cls = "vdc-bar-fill-neg" if is_neg else "vdc-bar-fill"
            html += (
                f'<div class="vdc-bar-row">'
                f'<div class="vdc-bar-name">{name}</div>'
                f'<div class="vdc-bar-track"><div class="{fill_cls}" style="width:{pct}%">{val}</div></div>'
                f'</div>\n'
            )

    elif ctype == "timeline":
        html += '<div class="vdc-tl">\n'
        for item in items:
            dt = _esc(item.get("date", ""))
            ev = _esc(item.get("event", item.get("text", "")))
            html += (
                f'<div class="vdc-tl-item"><div class="vdc-tl-dot"></div>'
                f'<div class="vdc-tl-date">{dt}</div>'
                f'<div class="vdc-tl-event">{ev}</div></div>\n'
            )
        html += '</div>\n'

    elif ctype == "highlights":
        for item in items:
            stat = _esc(item.get("stat", item.get("value", "")))
            text = _esc(item.get("text", item.get("label", "")))
            badge = f'<span class="vdc-badge">{stat}</span> ' if stat else ""
            html += (
                f'<div class="vdc-bullet">'
                f'<span class="vdc-bullet-arrow">›</span>'
                f'{badge}{text}</div>\n'
            )

    if source:
        html += f'<div class="vdc-footer">{source}</div>\n'

    html += '</div>'
    return html


def render_takeaways_html(takeaways):
    if not takeaways:
        return ""
    html = '<div class="vdc-takeaways">\n'
    html += '<div class="vdc-takeaways-title">Key Takeaways</div>\n<ul>\n'
    for t in takeaways:
        html += f'<li>{_esc(t)}</li>\n'
    html += '</ul>\n</div>'
    return html


def has_cards_already(body):
    return CARD_MARKER in body


def strip_old_cards(body):
    """Remove previously injected card blocks — both class-based and old inline-style versions."""
    # Class-based vdc cards
    body = re.sub(r'\n*<!-- data-card -->\s*<div class="vdc[^"]*"[\s\S]*?</div>\s*</div>\s*', '', body)
    body = re.sub(r'\n*<!-- data-card -->\s*<div class="vdc-takeaways[\s\S]*?</ul>\s*</div>\s*', '', body)
    # Old inline-style cards from v1
    body = re.sub(r'\n*<!-- data-card -->\s*<div style="background:#f9fafb[\s\S]*?</ul>\s*</div>\s*', '', body)
    body = re.sub(r'\n*<!-- data-card -->\s*<div style="background:linear-gradient[\s\S]*?</div>\s*</div>\s*', '', body)
    return body


def inject_cards_into_body(body, data_cards, key_takeaways):
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
        if hint in ("after_lead", "takeaways"):
            after_lead.append(rendered)
        elif hint == "before_conclusion":
            before_conclusion.append(rendered)
        else:
            mid_article.append(rendered)

    takeaways_html = ""
    if key_takeaways:
        takeaways_html = f'{CARD_MARKER}\n{render_takeaways_html(key_takeaways)}'

    insertions = {}

    # Takeaways + after_lead cards → prepended to top of body (right after hero image)
    prepend_blocks = []
    if takeaways_html:
        prepend_blocks.append(takeaways_html)
    prepend_blocks.extend(after_lead)

    # Mid-article cards → after ~60% of content
    if mid_article:
        mid_pos = max(int(n_content * 0.6), 3)
        mid_pos = min(mid_pos, n_content - 2)
        if mid_pos < 0:
            mid_pos = n_content - 1
        idx = content_indices[mid_pos] if mid_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(mid_article)

    # Before-conclusion cards → near end
    if before_conclusion:
        conc_pos = max(n_content - 3, int(n_content * 0.8))
        conc_pos = min(conc_pos, n_content - 1)
        idx = content_indices[conc_pos] if conc_pos < n_content else content_indices[-1]
        insertions.setdefault(idx, [])
        insertions[idx].extend(before_conclusion)

    # Build final body: prepend takeaways/after_lead at top, then body with mid/conclusion insertions
    result = []
    if prepend_blocks:
        result.append("\n\n".join(prepend_blocks))
        result.append("\n\n")
    for i, part in enumerate(paras):
        result.append(part)
        if i in insertions:
            result.append("\n\n")
            result.append("\n\n".join(insertions[i]))

    return "".join(result)


def fetch_articles(limit, since_hours, slug=None):
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
    r = requests.get(f"{SUPABASE_URL}/rest/v1/p2_articles", headers=HEADERS, params=params)
    r.raise_for_status()
    return r.json()


def patch_body(article_id, new_body):
    r = requests.patch(
        f"{SUPABASE_URL}/rest/v1/p2_articles?id=eq.{article_id}",
        headers={**HEADERS, "Content-Type": "application/json", "Prefer": "return=minimal"},
        json={"body": new_body, "cards_rendered_at": datetime.now(timezone.utc).isoformat()}
    )
    r.raise_for_status()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=50)
    ap.add_argument("--since-hours", type=int, default=6)
    ap.add_argument("--slug", help="Process a specific article by slug")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="Strip old cards and re-render")
    args = ap.parse_args()

    articles = fetch_articles(args.limit, args.since_hours, args.slug)
    print(f"📊 Found {len(articles)} enriched articles")

    rendered = skipped = errors = 0

    for art in articles:
        slug = art["slug"]
        body = art.get("body") or ""
        data_cards = art.get("data_cards") or []
        key_takeaways = art.get("key_takeaways") or []

        if not data_cards and not key_takeaways:
            skipped += 1; continue

        if has_cards_already(body) and not args.force:
            skipped += 1; continue

        # Strip old cards if re-rendering
        if has_cards_already(body):
            body = strip_old_cards(body)

        try:
            new_body = inject_cards_into_body(body, data_cards, key_takeaways)
            if new_body == body:
                skipped += 1; continue

            if args.dry_run:
                print(f"  ✅ [DRY] {slug} — {len(data_cards)} cards + {len(key_takeaways)} takeaways")
            else:
                patch_body(art["id"], new_body)
                print(f"  ✅ {slug} — {len(data_cards)} cards + {len(key_takeaways)} takeaways")
            rendered += 1
        except Exception as e:
            print(f"  ❌ {slug}: {e}", file=sys.stderr)
            errors += 1

    print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Done: {rendered} rendered, {skipped} skipped, {errors} errors")


if __name__ == "__main__":
    main()
