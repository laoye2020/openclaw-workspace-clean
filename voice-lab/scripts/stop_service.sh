#!/usr/bin/env bash
set -eo pipefail

ROOT="${HOME}/.openclaw/workspace/voice-lab"
PID_FILE="${ROOT}/service/server.pid"

if [[ ! -f "${PID_FILE}" ]]; then
  echo "No PID file found. Service appears stopped."
  exit 0
fi

pid="$(cat "${PID_FILE}" 2>/dev/null || true)"
if [[ -z "${pid}" ]]; then
  rm -f "${PID_FILE}"
  echo "Empty PID file removed."
  exit 0
fi

if ! kill -0 "${pid}" 2>/dev/null; then
  rm -f "${PID_FILE}"
  echo "Stale PID file removed (pid=${pid} not running)."
  exit 0
fi

kill "${pid}" 2>/dev/null || true
for _ in $(seq 1 20); do
  if ! kill -0 "${pid}" 2>/dev/null; then
    rm -f "${PID_FILE}"
    echo "CosyVoice2 service stopped (pid=${pid})."
    exit 0
  fi
  sleep 0.5
done

echo "Service did not stop gracefully; sending SIGKILL to pid=${pid}."
kill -9 "${pid}" 2>/dev/null || true
rm -f "${PID_FILE}"
echo "CosyVoice2 service stopped."
