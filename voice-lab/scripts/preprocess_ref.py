#!/usr/bin/env python3
import os, sys, subprocess, csv
from pathlib import Path
from pydub import AudioSegment

ROOT = Path(os.path.expanduser('~/.openclaw/workspace/voice-lab'))
REF = ROOT / 'ref' / 'sarafin_preview_ohoula.wav'
OUT_DIR = ROOT / 'ref' / 'chunks'
META = OUT_DIR / 'metadata.csv'

MIN_DUR = 3.0
MAX_DUR = 10.0
TARGET_LUFS = -20.0


def loudnorm(in_wav: Path, out_wav: Path, target_lufs: float = -20.0):
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        'ffmpeg','-y','-hide_banner','-loglevel','error',
        '-i', str(in_wav),
        '-af', f'loudnorm=I={target_lufs}:TP=-1.5:LRA=11',
        '-ar','16000','-ac','1',
        str(out_wav)
    ]
    subprocess.run(cmd, check=True)


def detect_silences(in_wav: Path):
    # Use silencedetect to get silence intervals
    cmd = [
        'ffmpeg','-i', str(in_wav), '-af', 'silencedetect=noise=-35dB:d=0.3',
        '-f','null','-'
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    out = proc.stderr
    sil_starts = []
    sil_ends = []
    for line in out.splitlines():
        line = line.strip()
        if 'silence_start:' in line:
            t = float(line.split('silence_start:')[1].strip())
            sil_starts.append(t)
        if 'silence_end:' in line and '| silence_duration:' in line:
            t = float(line.split('silence_end:')[1].split('|')[0].strip())
            sil_ends.append(t)
    # Build segments between silences
    # Get total duration
    audio = AudioSegment.from_wav(in_wav)
    total = audio.duration_seconds
    # Merge into intervals
    times = [0.0] + [v for pair in zip(sil_starts, sil_ends) for v in pair] + [total]
    times = sorted(set(times))
    # Pair consecutive times into candidate segments
    segs = []
    for i in range(0, len(times)-1, 2):
        s = times[i]
        e = times[i+1]
        if e - s >= 0.2:
            segs.append((s, e))
    # Merge small to reach MIN_DUR and cap at MAX_DUR
    merged = []
    cur_s, cur_e = None, None
    for s, e in segs:
        if cur_s is None:
            cur_s, cur_e = s, e
            continue
        if (cur_e - cur_s) < MIN_DUR and (e - cur_s) <= MAX_DUR:
            cur_e = e
        else:
            merged.append((cur_s, min(cur_e, cur_s+MAX_DUR)))
            cur_s, cur_e = s, e
    if cur_s is not None:
        merged.append((cur_s, min(cur_e, cur_s+MAX_DUR)))
    merged = [se for se in merged if (se[1]-se[0]) >= (MIN_DUR*0.6)]
    return merged


def save_segments(in_wav: Path, segs):
    audio = AudioSegment.from_wav(in_wav)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, (s, e) in enumerate(segs, start=1):
        seg = audio[s*1000:e*1000]
        out = OUT_DIR / f'chunk_{i:03d}.wav'
        seg.export(out, format='wav')
        rows.append([out.name, f"{(e-s):.2f}", ""])  # no text yet
        print(f'Saved {out} {(e-s):.2f}s')
    with open(META, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['file','duration','text'])
        w.writerows(rows)


def main():
    if not REF.exists():
        print(f"Missing reference file: {REF}", file=sys.stderr)
        sys.exit(1)
    norm = OUT_DIR.parent / 'sarafin_preview_ohoula.norm.wav'
    print('Loudness normalize...')
    loudnorm(REF, norm, TARGET_LUFS)
    print('Detecting silences and splitting...')
    segs = detect_silences(norm)
    save_segments(norm, segs)
    print(f'Metadata at {META}')

if __name__ == '__main__':
    main()
