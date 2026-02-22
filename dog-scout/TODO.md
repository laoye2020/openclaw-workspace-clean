# Roadmap TODO

## Day-2 (Completed)

- [x] Integrate pluggable LLM analyzer (`MockAnalyzer`, `DeepSeekAnalyzer`)
- [x] Blend model narrative score into final ranking with configurable weights
- [x] Persist analyzer confidence/rationale fields in `signals`
- [x] Add 5m/15m recheck scheduler with persistence tables
- [x] Re-score on recheck and emit summary status (`IMPROVING` / `WEAKENING` / `INVALIDATED`)
- [x] Add compact Chinese score timeline line in alerts
- [x] Add unit tests for merge/fallback/recheck transitions
- [x] Update README + env docs + Day-2 notes

## Next

- [ ] Risk provider upgrade (live honeypot/rug-check + cache + timeout)
- [ ] Retry/backoff for Dexscreener and Telegram
- [ ] Health endpoint / heartbeat metrics
- [ ] Docker + cron/systemd deployment template
- [ ] Trade feedback evaluator loop and weight auto-tuning
