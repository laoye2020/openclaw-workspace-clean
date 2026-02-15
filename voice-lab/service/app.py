#!/usr/bin/env python3
import io
import logging
import os
import sys
import random
import threading
import time
import uuid
from pathlib import Path
from typing import Optional, Tuple

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import Response
import uvicorn
import numpy as np
import soundfile as sf

ROOT = Path(os.path.expanduser('~/.openclaw/workspace/voice-lab'))
CHUNK_DIR = ROOT / 'ref' / 'chunks'
MODEL_DIR = ROOT / 'models'
SAMPLES_DIR = ROOT / 'samples'
ADAPTER = MODEL_DIR / 'sarafin_adapter.pt'
NUMBA_CACHE_DIR = ROOT / '.numba_cache'
SERAPHINE_REF_CANDIDATES = [
    ROOT / 'ref' / 'sarafin_preview_ohoula.norm.wav',
    ROOT / 'ref' / 'sarafin_preview_ohoula.wav',
]
DEFAULT_SERAPHINE_CHUNK = CHUNK_DIR / 'chunk_091.wav'

# Avoid librosa/numba cache crashes in constrained runtime environments.
os.environ.setdefault('NUMBA_DISABLE_JIT', '1')
os.environ.setdefault('NUMBA_CACHE_DIR', str(NUMBA_CACHE_DIR))
NUMBA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Ensure local CosyVoice repo is on path
LOCAL_REPO = ROOT / 'CosyVoice'
if (LOCAL_REPO / 'cosyvoice' / 'cli' / 'cosyvoice.py').exists():
    sys.path.insert(0, str(LOCAL_REPO))

app = FastAPI(title='CosyVoice2 TTS Service')

cv = None
cv_lock = threading.Lock()
logger = logging.getLogger(__name__)


def load_model():
    global cv
    with cv_lock:
        if cv is not None:
            return cv
        try:
            from cosyvoice.cli.cosyvoice import CosyVoice2

            model_id = os.environ.get('COSYVOICE2_MODEL', 'iic/CosyVoice2-0.5B')
            local_dir = MODEL_DIR / 'CosyVoice2-0.5B'
            if local_dir.exists():
                cv = CosyVoice2(model_dir=str(local_dir), load_vllm=False, fp16=False)
                return cv

            try:
                from huggingface_hub import snapshot_download as hf_snapshot

                path = hf_snapshot('FunAudioLLM/CosyVoice2-0.5B', local_dir=str(local_dir))
                cv = CosyVoice2(model_dir=str(path), load_vllm=False, fp16=False)
                return cv
            except Exception as hf_err:
                logger.warning('HuggingFace download failed, fallback to ModelScope: %s', hf_err)
                from modelscope import snapshot_download as ms_snapshot

                path = ms_snapshot(model_id, local_dir=str(local_dir))
                cv = CosyVoice2(model_dir=str(path), load_vllm=False, fp16=False)
                return cv
        except Exception as e:
            raise RuntimeError(f'Failed to load CosyVoice2: {e}')
    return cv


def pick_random_reference(max_sec=25.0):
    """Pick one prompt wav with valid duration."""
    files = sorted([p for p in CHUNK_DIR.glob('chunk_*.wav')])
    if not files:
        raise FileNotFoundError(f'No reference chunks found in {CHUNK_DIR}')
    random.shuffle(files)
    for f in files:
        try:
            dur = sf.info(str(f)).duration
        except Exception:
            dur = 0
        if 2.0 <= dur <= max_sec:
            return f
    return files[0]


def resolve_reference(prompt_wav: Optional[str], max_sec: float = 25.0) -> Path:
    def _valid_duration(path: Path) -> bool:
        try:
            dur = sf.info(str(path)).duration
        except Exception:
            return False
        return 2.0 <= dur <= 30.0 and dur <= max_sec

    if prompt_wav:
        ref_path = Path(os.path.expanduser(prompt_wav))
        if not ref_path.exists():
            raise FileNotFoundError(f'prompt_wav not found: {ref_path}')
        if not _valid_duration(ref_path):
            raise ValueError(f'prompt_wav duration must be between 2 and {min(30.0, max_sec):.1f} seconds: {ref_path}')
        return ref_path

    env_ref = os.environ.get('REFERENCE_WAV', '').strip()
    if env_ref:
        ref_path = Path(os.path.expanduser(env_ref))
        if ref_path.exists() and _valid_duration(ref_path):
            return ref_path

    for ref_path in SERAPHINE_REF_CANDIDATES:
        if ref_path.exists() and _valid_duration(ref_path):
            return ref_path

    if DEFAULT_SERAPHINE_CHUNK.exists() and _valid_duration(DEFAULT_SERAPHINE_CHUNK):
        return DEFAULT_SERAPHINE_CHUNK

    return pick_random_reference(max_sec=max_sec)


def build_instruct_text(style: str = 'seraphine', style_strength: float = 1.0) -> str:
    strength = max(0.6, min(1.4, float(style_strength)))
    if style.lower() == 'seraphine':
        mood = '更加闪亮热情' if strength >= 1.15 else '更自然克制'
        return (
            'You are a helpful assistant. '
            '请用萨勒芬妮风格中文表达：粉色、闪亮、可爱但靠谱，语气热情有音乐感，'
            f'情绪连贯、发音清晰，{mood}，句尾自然，避免机械停顿。<|endofprompt|>'
        )
    return (
        'You are a helpful assistant. '
        f'请用{style}风格表达，语气自然且情绪连贯，发音清晰。<|endofprompt|>'
    )


def _extract_chunk(raw_audio) -> np.ndarray:
    """Normalize model output shape into mono float32 ndarray."""
    if raw_audio is None:
        return np.array([], dtype=np.float32)
    if isinstance(raw_audio, (list, tuple)):
        if not raw_audio:
            return np.array([], dtype=np.float32)
        raw_audio = raw_audio[0]
    if hasattr(raw_audio, 'detach'):
        raw_audio = raw_audio.detach()
    if hasattr(raw_audio, 'cpu'):
        raw_audio = raw_audio.cpu()
    if hasattr(raw_audio, 'numpy'):
        raw_audio = raw_audio.numpy()

    arr = np.asarray(raw_audio, dtype=np.float32)
    arr = np.squeeze(arr)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim > 1:
        arr = arr.reshape(-1)
    return arr


def _to_wav_bytes(wav: np.ndarray, sample_rate: int) -> bytes:
    buf = io.BytesIO()
    sf.write(buf, wav, sample_rate, format='WAV', subtype='PCM_16')
    data = buf.getvalue()
    if len(data) <= 44:
        raise RuntimeError('Generated WAV payload is too small')
    return data


def _save_sample(wav: np.ndarray, sample_rate: int, prefix: str) -> Path:
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    stamp = int(time.time() * 1000)
    out_path = SAMPLES_DIR / f'{prefix}_{stamp}_{uuid.uuid4().hex[:8]}.wav'
    sf.write(str(out_path), wav, sample_rate, subtype='PCM_16')
    latest = SAMPLES_DIR / f'{prefix}_latest.wav'
    try:
        sf.write(str(latest), wav, sample_rate, subtype='PCM_16')
    except Exception:
        pass
    return out_path


def synthesize(
    text: str,
    save_prefix: str = 'speak',
    speed: float = 1.0,
    temperature: float = 0.8,
    top_p: float = 0.8,
    top_k: int = 25,
    style: str = 'seraphine',
    style_strength: float = 1.0,
    prompt_wav: Optional[str] = None,
    use_instruct2: bool = True,
    max_token_text_ratio: float = 20.0,
    min_token_text_ratio: float = 2.0,
) -> Tuple[bytes, Optional[Path]]:
    clean_text = text.strip()
    if not clean_text:
        raise ValueError('text cannot be empty')
    speed = float(speed)
    temperature = float(temperature)
    top_p = float(top_p)
    top_k = int(top_k)
    if speed <= 0:
        raise ValueError('speed must be > 0')
    if temperature <= 0:
        raise ValueError('temperature must be > 0')
    if not (0 < top_p <= 1):
        raise ValueError('top_p must be in (0, 1]')
    if top_k <= 0:
        raise ValueError('top_k must be > 0')

    model = load_model()
    ref = resolve_reference(prompt_wav, max_sec=float(os.environ.get('MAX_PROMPT_SEC', '25')))
    infer_kwargs = dict(
        stream=False,
        speed=speed,
        temperature=temperature,
        top_p=top_p,
        top_k=top_k,
        sampling=top_k,
        max_token_text_ratio=max_token_text_ratio,
        min_token_text_ratio=min_token_text_ratio,
    )
    try:
        wav_chunks = []
        if use_instruct2 and hasattr(model, 'inference_instruct2'):
            instruct_text = build_instruct_text(style=style, style_strength=style_strength)
            out_iter = model.inference_instruct2(
                tts_text=clean_text,
                instruct_text=instruct_text,
                prompt_wav=str(ref),
                **infer_kwargs,
            )
        else:
            prompt_text = os.environ.get('PROMPT_TEXT', '你好，我来啦。')
            if not prompt_text.strip():
                prompt_text = '你好，我来啦。'
            out_iter = model.inference_zero_shot(
                tts_text=clean_text,
                prompt_text=prompt_text,
                prompt_wav=str(ref),
                **infer_kwargs,
            )

        for out in out_iter:
            if not isinstance(out, dict):
                continue
            raw_audio = out.get('tts_speech')
            if raw_audio is None:
                raw_audio = out.get('speech')
            wav = _extract_chunk(raw_audio)
            if wav.size > 0:
                wav_chunks.append(wav)
        if not wav_chunks:
            raise RuntimeError('No audio returned from model')
        wav = np.concatenate(wav_chunks, axis=-1).astype(np.float32)
        if not np.isfinite(wav).all():
            raise RuntimeError('Model generated invalid numbers in audio output')
        peak = float(np.max(np.abs(wav))) if wav.size else 0.0
        if peak > 1.0:
            wav = wav / peak

        sample_rate = int(getattr(model, 'sample_rate', 24000))
        response_bytes = _to_wav_bytes(wav, sample_rate)
        saved_path = _save_sample(wav, sample_rate, prefix=save_prefix)
        logger.info(
            'synth ok prefix=%s ref=%s speed=%.3f temp=%.3f top_p=%.3f top_k=%d style=%s strength=%.2f',
            save_prefix,
            ref,
            speed,
            temperature,
            top_p,
            top_k,
            style,
            style_strength,
        )
        return response_bytes, saved_path
    except Exception as e:
        raise RuntimeError(f'Synthesis failed: {e}')


@app.get('/health')
async def health():
    return {'ok': True, 'model_loaded': cv is not None}


@app.get('/interfaces')
async def interfaces():
    return {
        'routes': ['/health', '/interfaces', '/speak', '/phase1'],
        'speak_params': {
            'text': 'required',
            'speed': {'default': 0.97, 'range': [0.8, 1.2]},
            'temperature': {'default': 0.72, 'range': [0.3, 1.5]},
            'top_p': {'default': 0.85, 'range': [0.5, 1.0]},
            'top_k': {'default': 28, 'range': [5, 80]},
            'style': {'default': 'seraphine'},
            'style_strength': {'default': 1.12, 'range': [0.6, 1.4]},
            'prompt_wav': 'optional absolute/relative path',
            'use_instruct2': {'default': True},
            'max_token_text_ratio': {'default': 20.0, 'range': [8.0, 40.0]},
            'min_token_text_ratio': {'default': 2.0, 'range': [0.5, 6.0]},
        },
    }


@app.get('/speak')
async def speak(
    text: Optional[str] = Query(default=None, description='Text to synthesize'),
    speed: float = Query(default=0.97, ge=0.8, le=1.2),
    temperature: float = Query(default=0.72, ge=0.3, le=1.5),
    top_p: float = Query(default=0.85, ge=0.5, le=1.0),
    top_k: int = Query(default=28, ge=5, le=80),
    style: str = Query(default='seraphine'),
    style_strength: float = Query(default=1.12, ge=0.6, le=1.4),
    prompt_wav: Optional[str] = Query(default=None),
    use_instruct2: bool = Query(default=True),
    max_token_text_ratio: float = Query(default=20.0, ge=8.0, le=40.0),
    min_token_text_ratio: float = Query(default=2.0, ge=0.5, le=6.0),
):
    if text is None:
        raise HTTPException(status_code=400, detail='text is required')
    try:
        payload, _ = synthesize(
            text,
            save_prefix='speak',
            speed=speed,
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            style=style,
            style_strength=style_strength,
            prompt_wav=prompt_wav,
            use_instruct2=use_instruct2,
            max_token_text_ratio=max_token_text_ratio,
            min_token_text_ratio=min_token_text_ratio,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(
        content=payload,
        media_type='audio/wav',
        headers={
            'Content-Disposition': 'inline; filename="speech.wav"',
            'Cache-Control': 'no-store',
        },
    )


@app.get('/phase1')
async def phase1():
    line = '老爷早上好～我是萨勒芬妮风格的豆芽，现在开始为你播报提醒。'
    try:
        payload, _ = synthesize(
            line,
            save_prefix='phase1',
            speed=0.97,
            temperature=0.72,
            top_p=0.85,
            top_k=28,
            style='seraphine',
            style_strength=1.12,
            use_instruct2=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return Response(
        content=payload,
        media_type='audio/wav',
        headers={'Content-Disposition': 'inline; filename="phase1.wav"'},
    )


def main():
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', '8006')))

if __name__ == '__main__':
    main()
