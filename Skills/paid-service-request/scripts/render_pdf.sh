#!/usr/bin/env bash
# Usage: render_pdf.sh <input.md> <output.pdf>
# Converts markdown → styled HTML → PDF via pandoc + python http server + playwright
set -euo pipefail

MD_FILE="$1"
PDF_FILE="$2"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CSS_FILE="$SKILL_DIR/assets/style.css"
TMPDIR=$(mktemp -d)
HTML_FILE="$TMPDIR/document.html"

# Find a free port
PORT=$(python3 -c "import socket; s=socket.socket(); s.bind(('',0)); print(s.getsockname()[1]); s.close()")

# Convert markdown to HTML with embedded CSS
CSS_CONTENT=$(cat "$CSS_FILE")
pandoc "$MD_FILE" -f markdown -t html5 --standalone \
  --metadata title=" " \
  -o "$HTML_FILE" 2>/dev/null

# Inject CSS into <head>
sed -i.bak "s|</head>|<style>${CSS_CONTENT}</style></head>|" "$HTML_FILE"
rm -f "$HTML_FILE.bak"

# Serve HTML
cd "$TMPDIR"
python3 -m http.server "$PORT" &>/dev/null &
SERVER_PID=$!
sleep 0.5

# Output for Claude to use with playwright
echo "RENDER_URL=http://localhost:${PORT}/document.html"
echo "RENDER_PDF=$PDF_FILE"
echo "SERVER_PID=$SERVER_PID"
echo "TMPDIR=$TMPDIR"
