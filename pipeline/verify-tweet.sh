#!/bin/bash
# Verify a tweet ID exists and return its data
# Usage: verify-tweet.sh TWEET_ID
# Returns: exit 0 + JSON if valid, exit 1 if not found

TWEET_ID="$1"
if [ -z "$TWEET_ID" ]; then
  echo "Usage: verify-tweet.sh TWEET_ID" >&2
  exit 1
fi

RESPONSE=$(curl -s "https://react-tweet.vercel.app/api/tweet/$TWEET_ID" 2>/dev/null)
HAS_DATA=$(echo "$RESPONSE" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    if d.get('data') is not None:
        text = d['data'].get('text','')[:100]
        user = d['data'].get('user',{}).get('screen_name','?')
        photos = len([m for m in d['data'].get('mediaDetails',[]) if m.get('type')=='photo'])
        videos = len([m for m in d['data'].get('mediaDetails',[]) if m.get('type')=='video'])
        print(f'VALID|@{user}|photos={photos}|videos={videos}|{text}')
    else:
        print('NOT_FOUND')
except:
    print('ERROR')
" 2>/dev/null)

if [[ "$HAS_DATA" == VALID* ]]; then
  echo "$HAS_DATA"
  exit 0
else
  echo "$HAS_DATA"
  exit 1
fi
