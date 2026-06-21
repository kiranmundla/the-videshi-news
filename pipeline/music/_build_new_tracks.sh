#!/usr/bin/env bash
# Build new CC-BY tracks into the library: normalize loudness to ~-19dB mean,
# write full + 30s + 15s cuts matching existing naming/fade convention.
set -euo pipefail
TMP=/tmp
DEST="$HOME/workspace/the-videshi-news/pipeline/music"
TARGET_MEAN=-19.0   # match existing library RMS mean

# tmpfile|family|slug|start_sec   (start = where to begin the short cut, a strong section)
ENTRIES=(
  "ic_tech1|tech-corporate|the-show-must-be-go|30"
  "ic_tech2|tech-corporate|digital-lemonade|20"
  "ic_tech3|tech-corporate|cipher|24"
  "ic_dark1|dramatic-dark|anxiety|10"
  "ic_dark2|dramatic-dark|darkest-child|30"
  "ic_anth1|anthemic-triumph|rising-tide|40"
  "ic_anth2|anthemic-triumph|heroic-age|8"
  "ic_anth3|anthemic-triumph|eternal-hope|45"
  "ic_anth4|anthemic-triumph|exhilarate|20"
  "ic_epic1|cinematic-epic|crossing-the-chasm|30"
  "ic_epic3|cinematic-epic|killers|40"
  "ic_news1|breaking-news|investigations|6"
  "ic_news2|breaking-news|newer-wave|18"
)

gain_for() {  # arg: filepath -> echoes "volume=Xdb"
  local mv
  mv=$(ffmpeg -hide_banner -i "$1" -af volumedetect -f null /dev/null 2>&1 \
        | grep mean_volume | grep -oE '\-?[0-9.]+' | head -1)
  python3 -c "print(f'{($TARGET_MEAN)-($mv):.1f}')"
}

for e in "${ENTRIES[@]}"; do
  IFS='|' read -r tmp fam slug start <<< "$e"
  src="$TMP/$tmp.mp3"
  [ -f "$src" ] || { echo "MISSING $src"; continue; }
  g=$(gain_for "$src")
  base="$fam-$slug"
  # full (normalized, re-encoded at 256k to match library)
  ffmpeg -hide_banner -loglevel error -y -i "$src" -af "volume=${g}dB" \
    -c:a libmp3lame -b:a 256k "$DEST/$base.mp3"
  # 30s cut: from strong section, 1s fade in / 1.5s fade out
  ffmpeg -hide_banner -loglevel error -y -ss "$start" -t 30 -i "$src" \
    -af "volume=${g}dB,afade=t=in:st=0:d=1,afade=t=out:st=28.5:d=1.5" \
    -c:a libmp3lame -b:a 192k "$DEST/$base-30s.mp3"
  # 15s cut
  ffmpeg -hide_banner -loglevel error -y -ss "$start" -t 15 -i "$src" \
    -af "volume=${g}dB,afade=t=in:st=0:d=0.8,afade=t=out:st=13.7:d=1.3" \
    -c:a libmp3lame -b:a 192k "$DEST/$base-15s.mp3"
  echo "built $base  (gain ${g}dB)"
done
echo "DONE"
