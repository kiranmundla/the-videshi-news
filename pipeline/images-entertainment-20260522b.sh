#!/bin/bash
# Image sourcing for entertainment articles — May 22 2026 batch 2
set -euo pipefail

source ~/.env.supabase
PEXELS_KEY=$(grep PEXELS_API_KEY ~/workspace/.env.pexels | cut -d= -f2)
BUCKET="article-images"

fetch_and_upload() {
    local ARTICLE_ID="$1"
    local QUERY="$2"
    local FILENAME="${ARTICLE_ID}.jpg"

    echo "🔍 Searching Pexels: '$QUERY' for $ARTICLE_ID"

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

# Article 1: Karuppu — Tamil cinema, temple, deity
fetch_and_upload "2dd9b252-4fb7-4ec5-a3da-6133de148329" "Indian temple deity dramatic"

# Article 2: Dhurandhar — spy thriller streaming
fetch_and_upload "c53c1537-8e94-49d0-93db-48be95db40de" "spy thriller silhouette dark"

# Article 3: Star Wars vs India — empty cinema
fetch_and_upload "d684dc5f-7f6e-4369-9906-e9af57a6726f" "empty movie theater seats"

echo ""
echo "🎬 Image sourcing complete!"
