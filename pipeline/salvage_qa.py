#!/usr/bin/env python3
"""Salvage a completed Shotstack render whose QA gate failed due to a transient
network error. Re-runs ONLY the QA gate on the already-rendered file (no
re-render). If it passes, uploads to Supabase and registers in prebuilt_reels.

Usage: python3 salvage_qa.py <article_id> <video_path> [poster_path] [thumb_path]
"""
import sys, os, importlib.util

# Capture real args BEFORE clobbering sys.argv for the module import
_args = sys.argv[1:]
article_id = _args[0]
video_path = _args[1]
poster_path = _args[2] if len(_args) > 2 else None
thumb_path = _args[3] if len(_args) > 3 else None

spec = importlib.util.spec_from_file_location("ssr", "shotstack-reel.py")
m = importlib.util.module_from_spec(spec)
sys.argv = ["ssr"]  # prevent argparse in main from running
spec.loader.exec_module(m)
import requests

# Fetch article
r = requests.get(
    f"{m.SB_URL}/rest/v1/p2_articles",
    headers=m.SB_HEADERS,
    params={"id": f"eq.{article_id}",
            "select": "id,headline,subheadline,slug,category,vertical,body,image_url,published_at"},
    timeout=15,
)
article = r.json()[0]
print(f"Article: {article['headline'][:70]}")

# Already registered?
slugs, ids = m.get_existing_reel_slugs()
if article["id"] in ids or article.get("slug") in slugs:
    print("⏭️  Already registered in prebuilt_reels — nothing to do.")
    sys.exit(0)

# Reuse cached script
script_data = m.generate_script(article)

# Re-run QA gate ONLY (no re-render)
print("\n🔍 Re-running QA gate on existing render...")
qa_passed, qa_score, qa_notes = m.run_qa_gate(video_path, article, script_data)
if not qa_passed:
    print(f"❌ QA still failed (score: {qa_score}) — {qa_notes}")
    sys.exit(2)
print(f"✅ QA PASSED (score: {qa_score})")

# Upload + register (mirror run_anchor_reel tail)
final_name = os.path.basename(video_path)
print("\n☁️ Uploading final reel...")
video_url, uploaded_video_path = m.upload_final_reel(video_path, final_name)

uploaded_poster_url = None
uploaded_thumb_url = None
if poster_path and os.path.exists(poster_path):
    uploaded_poster_url = m.upload_asset(poster_path, f"reels/posters/{os.path.basename(poster_path)}", "image/jpeg")
if thumb_path and os.path.exists(thumb_path):
    uploaded_thumb_url = m.upload_asset(thumb_path, f"reels/thumbnails/{os.path.basename(thumb_path)}", "image/jpeg")

if video_url:
    print("\n📋 Registering reel...")
    caption = m.build_caption(article)
    ok = m.register_reel(article, video_url, str(uploaded_video_path), caption,
                         poster_url=uploaded_poster_url, thumbnail_url=uploaded_thumb_url,
                         qa_score_actual=qa_score)
    print(f"\n{'='*50}\nSALVAGE {'COMPLETE' if ok else 'FAILED at registration'}")
    print(f"  Supabase URL: {video_url}")
    sys.exit(0 if ok else 3)
else:
    print("❌ Upload failed")
    sys.exit(4)
