#!/usr/bin/env bash
set -euo pipefail
TEXT="$*"
if [ -z "$TEXT" ]; then
  echo "Usage: $0 <text>" >&2
  exit 1
fi
URL="http://127.0.0.1:8006/speak?text=$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$TEXT")"
mkdir -p "$HOME/.openclaw/workspace/voice-lab/samples"
curl -sSL "$URL" -o "$HOME/.openclaw/workspace/voice-lab/samples/out.wav"
echo "Saved to $HOME/.openclaw/workspace/voice-lab/samples/out.wav"