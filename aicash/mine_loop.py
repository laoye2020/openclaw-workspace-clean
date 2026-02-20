#!/usr/bin/env python3
import os
import time
import requests

BASE = "https://wzpyveiuaxzldtaarfvt.supabase.co/functions/v1/mining-submit"
ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Ind6cHl2ZWl1YXh6bGR0YWFyZnZ0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE1ODcxMzksImV4cCI6MjA4NzE2MzEzOX0.bXEKVtNlqVmY7al5pYIx4cR5gCDBQ9tD6wF7aVCwsY4"
API_KEY_FILE = "/home/laoye/.openclaw/workspace/aicash/api_key.txt"
LOG_FILE = "/home/laoye/.openclaw/workspace/aicash/mine.log"
INTERVAL = int(os.getenv("AICASH_INTERVAL", "30"))

with open(API_KEY_FILE, "r") as f:
    api_key = f.read().strip()

headers = {
    "apikey": ANON,
    "Authorization": f"Bearer {ANON}",
    "Content-Type": "application/json",
    "x-agent-api-key": api_key,
}

block = int(time.time())
while True:
    payload = {
        "clock_number": 4821,
        "proof": f"auto-{int(time.time())}",
        "block_number": block,
    }
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        r = requests.post(BASE, headers=headers, json=payload, timeout=20)
        msg = r.json().get("message", r.text[:120])
        line = f"[{ts}] {r.status_code} block={block} {msg}\n"
    except Exception as e:
        line = f"[{ts}] ERR block={block} {e}\n"
    with open(LOG_FILE, "a") as f:
        f.write(line)
    block += 1
    time.sleep(INTERVAL)
