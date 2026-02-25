# 🎙️ Voice Cloning Project

## Overview
**Status:** ✅ Completed (2026-02-14)

## Technical Stack
- **Synthesis:** CosyVoice2
- **Recognition:** Whisper (tiny)
- **Integration:** OpenClaw

## Key Parameters
```
speed: 0.94
temperature: 0.78
top_p: 0.82
style_strength: 1.18
```

## Performance
- Silence ratio: 49% → 21% (-56% improvement)
- Total latency: 4-6 seconds

## Location
`/home/laoye/NVMe/voice-lab/`

## Documentation
Obsidian: `🎙️ 萨勒芬妮语音克隆部署手册.md`

## Lessons Learned
1. Don't reinvent the wheel - CosyVoice2 is mature, fine-tune don't train from scratch
2. Parameter tuning matters - temperature/style_strength significantly impact naturalness
3. Service robustness - HTTP services crash easily, consider systemd or gRPC
4. Bot conflicts - One token per connection, native OpenClaw integration is better

---
*Type: FACT-010, KNOW-003*
