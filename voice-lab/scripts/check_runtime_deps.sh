#!/usr/bin/env bash
set -eo pipefail

ROOT="${HOME}/.openclaw/workspace/voice-lab"
source "${ROOT}/scripts/activate.sh"

python - <<'PY'
import importlib
from importlib import metadata

required = [
    "fastapi",
    "uvicorn",
    "numpy",
    "soundfile",
    "torch",
    "torchaudio",
    "transformers",
    "huggingface_hub",
    "modelscope",
    "omegaconf",
    "hydra",
    "hyperpyyaml",
    "conformer",
    "diffusers",
    "onnxruntime",
    "whisper",
    "librosa",
    "inflect",
    "wget",
    "tqdm",
]

training_extras = [
    "deepspeed",
    "lightning",
    "pytorch-lightning",
    "tensorboard",
    "gradio",
]

missing = []
for module_name in required:
    try:
        importlib.import_module(module_name)
    except Exception as exc:
        missing.append((module_name, str(exc)))

if missing:
    print("Missing runtime modules:")
    for name, err in missing:
        print(f" - {name}: {err}")
    raise SystemExit(1)

installed = {dist.metadata["Name"].lower() for dist in metadata.distributions()}
present_extras = [pkg for pkg in training_extras if pkg in installed]

print("Runtime dependency check: OK")
if present_extras:
    print("Note: training-oriented packages detected (not required for inference):")
    for pkg in present_extras:
        print(f" - {pkg}")
PY
