#!/bin/bash
# Image sourcing for entertainment articles — May 22 2026
set -euo pipefail

source ~/.env.supabase
PEXELS_KEY=$(cat ~/workspace/.env.pexels | grep PEXELS_API_KEY | cut -d= -f2)
BUCKET="article-images"

fetch_and_upload() {
    local ARTICLE_ID="$1"
    local QUERY="$2"
    local FILENAME="${ARTICLE_ID}.jpg"

    echo "🔍 Searching Pexels: '$QUERY' for $ARTICLE_ID"

    # Search Pexels
    local PHOTO_URL
    PHOTO_URL=$(curl -sS "https://api.pexels.com/v1/search?query=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$QUERY'))")&per_page=5&orientation=landscape" \
        -H "Authorization: $PEXELS_KEY" | python3 -c "
import json, sys
data = json.load(sys.stdin)
photos = data.get('photos', [])
if photos:
    print(photos[0]['src']['landscape'])
else:
    print('')
")

    if [ -z "$PHOTO_URL" ]; then
        echo "⚠️  No Pexels result for: $QUERY"
        return 1
    fi

    echo "📥 Downloading: $PHOTO_URL"
    curl -sS -o "/tmp/$FILENAME" "$PHOTO_URL"

    # Upload to Supabase Storage
    echo "📤 Uploading to Supabase: $FILENAME"
    local UPLOAD_URL="$SUPABASE_URL/storage/v1/object/$BUCKET/$FILENAME"
    local STATUS
    STATUS=$(curl -sS -o /dev/null -w "%{http_code}" -X POST "$UPLOAD_URL" \
        -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
        -H "Content-Type: image/jpeg" \
        -H "x-upsert: true" \
        --data-binary "@/tmp/$FILENAME")

    if [ "$STATUS" = "200" ] || [ "$STATUS" = "201" ]; then
        local PUBLIC_URL="$SUPABASE_URL/storage/v1/object/public/$BUCKET/$FILENAME"
        echo "✅ Uploaded: $PUBLIC_URL"

        # Update article
        curl -sS -X PATCH "$SUPABASE_URL/rest/v1/p2_articles?id=eq.$ARTICLE_ID" \
            -H "apikey: $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Authorization: Bearer $SUPABASE_SERVICE_ROLE_KEY" \
            -H "Content-Type: application/json" \
            -d "{\"image_url\": \"$PUBLIC_URL\", \"image_attribution\": \"The Videshi\"}"
        echo "✅ Updated article image_url"
    else
        echo "❌ Upload failed with status $STATUS"
    fi

    rm -f "/tmp/$FILENAME"
}

# Article 1: Drishyam 3 — movie theater India
fetch_and_upload "ae9e2d08-c1a6-4c4c-832a-979ca8b0cc5c" "Indian movie theater cinema audience"

# Article 2: Dhurandhar — streaming TV
fetch_and_upload "dee989cc-7d3c-49fd-b395-2bfbcd65bf2f" "streaming service television remote"

# Article 3: Cannes — film festival red carpet
fetch_and_upload "7ae5eed2-b964-43c2-bab6-a1a0c420122f" "Cannes film festival red carpet"

# Article 4: Chand Mera Dil — Bollywood romance
fetch_and_upload "828b0000-f853-4ab4-b4b9-f98e80e2030e" "Bollywood couple romantic"

echo ""
echo "🎬 Image sourcing complete!"
