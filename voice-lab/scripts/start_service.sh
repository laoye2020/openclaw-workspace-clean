#!/usr/bin/env bash
set -eo pipefail

ROOT="${HOME}/.openclaw/workspace/voice-lab"
APP="${ROOT}/service/app.py"
LOG="${ROOT}/service/server.log"
PID_FILE="${ROOT}/service/server.pid"
PORT="${PORT:-8006}"
NUMBA_CACHE_DIR="${NUMBA_CACHE_DIR:-${ROOT}/.numba_cache}"

mkdir -p "${ROOT}/service"
mkdir -p "${NUMBA_CACHE_DIR}"

if [[ -f "${PID_FILE}" ]]; then
  old_pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
  if [[ -n "${old_pid}" ]] && kill -0 "${old_pid}" 2>/dev/null; then
    echo "CosyVoice2 service already running (pid=${old_pid}, port=${PORT})"
    exit 0
  fi
  rm -f "${PID_FILE}"
fi

source "${ROOT}/scripts/activate.sh"
export NUMBA_DISABLE_JIT="${NUMBA_DISABLE_JIT:-1}"
export NUMBA_CACHE_DIR

nohup python "${APP}" >> "${LOG}" 2>&1 &
new_pid=$!
echo "${new_pid}" > "${PID_FILE}"

sleep "${START_WAIT_SECONDS:-2}"
if ! kill -0 "${new_pid}" 2>/dev/null; then
  echo "Failed to start CosyVoice2 service. Recent logs:" >&2
  tail -n 80 "${LOG}" >&2 || true
  exit 1
fi

echo "CosyVoice2 service started (pid=${new_pid}, port=${PORT})"
echo "Log file: ${LOG}"
