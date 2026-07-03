# The Videshi — Database Audit

**Run date:** 2026-07-03 14:27 PDT (21:27 UTC)

---

## Articles (p2_articles)

| Metric | Count | Status |
|---|---|---|
| **Total published** | 6,481 | — |
| **Published last 24h** | 128 | ✅ Active publishing |
| **Published last 7 days** | 902 | ✅ ~129/day average |
| **Missing hero image** | 158 | ⚠️ 2.4% of published |
| **Null published_at** | 0 | ✅ Clean |
| **Missing subheadline** | 18 | ⚠️ Minor (0.3%) |
| **Very short body (<200 chars)** | 0 | ✅ Clean |
| **Double-encoded sources** | 25 | ⚠️ 0.4% have escaped JSON |

### Latest 5 Published Articles
All published at 2026-07-03 ~21:15–21:16 UTC:

1. **India Just Logged Its Driest June in Fifteen Years. The Next Two Weeks Will Decide What Millions of Farmers Eat.** — 2026-07-03 21:16:06 UTC
2. **Every AI Lab Wants Its Own Chip Now. The Race to Dethrone Nvidia Just Got Three-Way.** — 2026-07-03 21:15:47 UTC
3. **India's Central Bank Just Called AI the Biggest Cyber Threat to Banking. Here's What That Means for Your Money.** — 2026-07-03 21:15:40 UTC
4. **She Beat Myositis, Rebuilt Her Career, and Married the Man Behind The Family Man. Now Samantha Is Becoming a Mother.** — 2026-07-03 21:15:33 UTC
5. **Dhurandhar Just Crossed ₹3,100 Crore. Now It's Coming for Japan.** — 2026-07-03 21:15:16 UTC

---

## Events

| Metric | Value | Status |
|---|---|---|
| **Future events (end_date > now)** | 177 | ✅ Healthy backlog |
| **Earliest future event start** | 2026-07-03 | ✅ Current |
| **Latest future event end** | 2027-04-30 | ✅ Good coverage |

> **Note:** The `events` table uses `date` (start) and `end_date` columns, not `event_date`.

---

## Directory Listings

| Metric | Count | Status |
|---|---|---|
| **Total listings** | 3,939 | — |
| **Expired Google photo_reference URLs** | 3,094 | 🔴 78.5% — critical |
| **Supabase storage images** | 383 | 9.7% migrated |

> **Critical issue:** 3,094 of 3,939 directory listings (78.5%) still use Google Places `photo_reference` tokens in their `image_url`. These tokens expire, so most of these images are likely broken. Only 383 (9.7%) have been migrated to Supabase storage. The remaining ~462 listings may have other image sources or be missing images entirely.

---

## Classifieds

| Metric | Count |
|---|---|
| **Total classifieds** | 44 |

---

## Issues Summary

### 🔴 Critical
- **Directory images:** 3,094 / 3,939 listings (78.5%) have expired Google `photo_reference` tokens. Needs a bulk migration to Supabase storage or a permanent image source.

### ⚠️ Moderate
- **Missing hero images:** 158 published articles (2.4%) have no `image_url`. These render without a hero on the site.
- **Double-encoded sources:** 25 articles have JSON sources with escaped backslashes/quotes, likely from double-serialization during ingestion.

### ℹ️ Minor
- **Missing subheadlines:** 18 articles (0.3%) lack a subheadline.

### ✅ Healthy
- Publishing cadence is strong: 128 articles in the last 24h, 902 in the last 7 days.
- No articles with null `published_at` or very short bodies.
- 177 future events spanning through April 2027.
- Latest articles were published minutes ago — pipeline is active.
