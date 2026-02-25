# ☁️ Server Infrastructure

## Xiaomi Calendar Sync
**Status:** ✅ Completed (2026-02-08)

### Configuration
- **Calendar URL:** https://laoye2025.top/calendar.ics
- **Server:** 47.107.58.190 (Aliyun)
- **Domain:** laoye2025.top (Cloudflare)
- **File Location:** /usr/share/nginx/html/calendar.ics
- **Subscription:** Xiaomi Phone Calendar → URL subscription

### Reminder System
- **05:00** - Morning meditation
- **05:20** - Face massage
- **05:30** - Morning workout
- **22:00** - Evening check-in
- **Format:** Reply "开始" / "完成" / "跳过"

## OpenClaw Setup

### Memory System
- **Embedding:** OpenRouter API (OpenAI compatible)
- **Vector DB:** Local Qdrant (Docker: openclaw-qdrant)
- **Framework:** openclaw-mem0
- **Status:** Self-hosted, zero quota anxiety

### Model Configuration
- **Default:** kimi-coding/k2p5
- **Fallback:** openai-codex/gpt-5.3-codex
- **Context:** 400k tokens
- **Compaction:** safeguard mode

---
*Type: FACT-003, FACT-006, FACT-007, infrastructure memory*
