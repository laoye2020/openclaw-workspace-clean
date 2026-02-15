#!/usr/bin/env python3
import os
from pathlib import Path
import argparse
import csv

ROOT = Path(os.path.expanduser('~/.openclaw/workspace/voice-lab'))
CHUNK_DIR = ROOT / 'ref' / 'chunks'
DATASET_DIR = ROOT / 'dataset'


def run_whisper(model_size='large-v3'):
    import whisper
    model = whisper.load_model(model_size)
    pairs = []
    for wav in sorted(CHUNK_DIR.glob('chunk_*.wav')):
        print(f"Transcribing {wav.name}...")
        result = model.transcribe(str(wav), language='zh')
        text = result.get('text','').strip()
        if not text:
            continue
        out_wav = DATASET_DIR / wav.name
        out_wav.parent.mkdir(parents=True, exist_ok=True)
        # copy file
        out_wav.write_bytes(Path(wav).read_bytes())
        pairs.append((out_wav.name, text))
    with open(DATASET_DIR / 'metadata.csv', 'w', newline='') as f:
        w = csv.writer(f, delimiter='|')
        for fpath, t in pairs:
            w.writerow([fpath, t])
    print(f"Wrote {len(pairs)} pairs to {DATASET_DIR/'metadata.csv'}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--model', default='large-v3', help='whisper model size (large-v3, medium, small)')
    args = ap.parse_args()
    run_whisper(args.model)

if __name__ == '__main__':
    main()
