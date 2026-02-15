# CosyVoice2 Local Service Runbook

## 1) Activate Environment

```bash
cd ~/.openclaw/workspace/voice-lab
source scripts/activate.sh
```

## 2) Runtime Dependency Check (Inference Only)

```bash
bash scripts/check_runtime_deps.sh
```

Runtime package baseline is pinned in:

- `requirements.runtime.txt`

Optional cleanup of training-only packages (if you want a leaner runtime):

```bash
python -m pip uninstall -y deepspeed lightning pytorch-lightning tensorboard gradio
```

## 3) Start Service

```bash
cd ~/.openclaw/workspace/voice-lab
bash scripts/start_service.sh
```

Expected output:

- `CosyVoice2 service started (pid=..., port=8006)`

Log file:

- `~/.openclaw/workspace/voice-lab/service/server.log`

## 4) Stop Service

```bash
cd ~/.openclaw/workspace/voice-lab
bash scripts/stop_service.sh
```

## 5) API Smoke Tests

```bash
curl -sS http://127.0.0.1:8006/health
```

Expected:

```json
{"ok":true,"model_loaded":false}
```

Generate short audio:

```bash
curl -sS -o /tmp/speak_test.wav "http://127.0.0.1:8006/speak?text=测试"
file /tmp/speak_test.wav
ls -lh /tmp/speak_test.wav
```

Expected:

- HTTP 200
- WAV file is non-empty

## 6) Generate Long Demo (Telegram)

Current generated demo file:

- `~/.openclaw/workspace/voice-lab/samples/long_demo.wav`

Verify size + duration:

```bash
ls -lh ~/.openclaw/workspace/voice-lab/samples/long_demo.wav
python - <<'PY'
import soundfile as sf
p='~/.openclaw/workspace/voice-lab/samples/long_demo.wav'
import os
p=os.path.expanduser(p)
info=sf.info(p)
print({'duration_sec': round(info.duration,2), 'samplerate': info.samplerate, 'size_bytes': os.path.getsize(p)})
PY
```

## 7) Troubleshooting

- If `/speak` returns 500 with librosa/numba cache errors:
  - Ensure `NUMBA_DISABLE_JIT=1` (already set by `start_service.sh` and `service/app.py`).
- If old PID exists but process is gone:
  - `bash scripts/stop_service.sh` (removes stale pid file).
- If model loading fails:
  - Check local model dir exists: `models/CosyVoice2-0.5B/`
  - Check logs: `tail -n 120 service/server.log`
