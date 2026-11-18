#!/usr/bin/env bash
# Render G-DESIGN/exports/v4/*.render.html to PNG at 2x (2400 px wide) with headless Firefox.
# Usage: bash export_png.sh   (needs python3 + firefox; run build_v4.py first)
set -euo pipefail
cd "$(dirname "$0")/../exports/v4"
PROFILE="$(mktemp -d)"
# 2x: the wrapper stretches the SVG to the window width, the window is twice the native size
python3 -m http.server 8769 --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!
trap 'kill $SRV; rm -rf "$PROFILE"' EXIT
sleep 1
for f in *.render.html; do
  name="${f%.render.html}"
  read -r W H < <(python3 -c "import re,sys;m=re.search(r'viewBox=\"0 0 ([0-9.]+) ([0-9.]+)\"',open('$name.svg').read());print(int(float(m[1])),int(float(m[2])))")
  timeout 90 firefox --headless --profile "$PROFILE" --no-remote --window-size="$((W*2)),$((H*2))" --screenshot "$PWD/$name.png" "http://127.0.0.1:8769/$f" >/dev/null 2>&1 || true
  echo "$name.png"
done
