#!/usr/bin/env bash
# Source images for 4 news articles using curl
set -euo pipefail

source ~/.env.supabase
source ~/workspace/.env.pexels

# Article configs: id | search_query
declare -A ARTICLE_SEARCHES
ARTICLE_SEARCHES[ce26260a-c726-447d-ba74-ccc8916ffcec]="Indian trucks highway traffic"
ARTICLE_SEARCHES[991448e3-f255-4612-bd6f-57c6e25c9f9c]="Hindu temple London"
ARTICLE_SEARCHES[d5410792-507a-4e01-8e01-dd80247fed93]="bhangra dance celebration"
ARTICLE_SEARCHES[484f90c4-3009-471e-8f9c-6d800fee620f]="India military soldiers"

declare -A ARTICLE_NAMES
ARTICLE_NAMES[ce26260a-c726-447d-ba74-ccc8916ffcec]="India Fuel Shortage"
ARTICLE_NAMES[991448e3-f255-4612-bd6f-57c6e25c9f9c]="UK Anti-Hindu Hate Monitor"
ARTICLE_NAMES[d5410792-507a-4e01-8e01-dd80247fed93]="Bhangra Habs Jerseys"
ARTICLE_NAMES[484f90c4-3009-471e-8f9c-6d800fee620f]="India-South Korea Defense"

for AID in "${!ARTICLE_SEARCHES[@]}"; do
    QUERY="${ARTICLE_SEARCHES[$AID]}"
    NAME="${ARTICLE_NAMES[$AID]}"
    echo ""
    echo "════════════════════════════════════════"
    echo "📸 $NAME ($AID)"
    echo "════════════════════════════════════════"
    
    # Search Pexels
    ENCODED_QUERY=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")
    RESULT=$(curl -s "https://api.pexels.com/v1/search?query=$ENCODED_QUERY&per_page=3&orientation=landscape" \
        -H "Authorization: $PEXELS_API_KEY" 2>/dev/null)
    
    IMAGE_URL=$(echo "$RESULT" | python3 -c "
import json, sys
data = json.load(sys.stdin)
photos = data.get('photos', [])
if photos:
    print(photos[0]['src'].get('large2x') or photos[0]['src'].get('large'))
else:
    print('')
" 2>/dev/null)
    
    if [ -z "$IMAGE_URL" ]; then
        echo "  ❌ No image found — skipping"
        continue
    fi
    
    echo "  🔍 Found: $IMAGE_URL"
    
    # Download
    TMP="/tmp/${AID}.jpg"
    curl -sL "$IMAGE_URL" -o "$TMP" 2>/dev/null
    SIZE=$(stat -c%s "$TMP" 2>/dev/null || echo 0)
    echo "  ⬇️  Downloaded: ${SIZE} bytes"
    
    if [ "$SIZE" -lt 1000 ]; then
        echo "  ❌ Download too small — skipping"
        rm -f "$TMP"
        continue
    fi
    
    # Upload to Supabase Storage
    UPLOAD_RESULT=$(curl -s -w '\n%{http_code}' \
        -X POST "$SUPABASE_URL/storage/v1/object/article-images/${AID}.jpg" \
        -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: image/jpeg" \
        -H "x-upsert: true" \
        --data-binary @"$TMP" 2>/dev/null)
    
    HTTP_CODE=$(echo "$UPLOAD_RESULT" | tail -1)
    echo "  ⬆️  Upload HTTP: $HTTP_CODE"
    
    if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "201" ]; then
        PUBLIC_URL="$SUPABASE_URL/storage/v1/object/public/article-images/${AID}.jpg"
        
        # Update article in DB
        curl -s -X PATCH "$SUPABASE_URL/rest/v1/p2_articles?id=eq.$AID" \
            -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Content-Type: application/json" \
            -H "Prefer: return=minimal" \
            -d "{\"image_url\": \"$PUBLIC_URL\", \"image_attribution\": \"The Videshi\"}" >/dev/null 2>&1
        
        echo "  ✅ Image set: $PUBLIC_URL"
    else
        echo "  ❌ Upload failed"
    fi
    
    rm -f "$TMP"
done

echo ""
echo "════════════════════════════════════════"
echo "Image sourcing complete."
echo "════════════════════════════════════════"
