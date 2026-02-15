#!/usr/bin/env bash
set -euo pipefail
ROOT="$HOME/.openclaw/workspace/voice-lab"
source <(micromamba shell hook -s bash)
micromamba activate voice-lab

# Placeholder: try to call CosyVoice finetune if available
DATA_DIR="$ROOT/dataset"
OUT="$ROOT/models/sarafin_adapter.pt"

if [ ! -f "$ROOT/CosyVoice/finetune/train_adapter.py" ]; then
  echo "CosyVoice finetune script not found. Please update repo or paths." >&2
  exit 1
fi

python "$ROOT/CosyVoice/finetune/train_adapter.py" \
  --data "$DATA_DIR/metadata.csv" \
  --output "$OUT" \
  --epochs 2 \
  --batch_size 4 \
  --lr 1e-4 \
  --devices 1

echo "Saved adapter to $OUT"