# dog-scout (土狗早筛系统) - Day-2

Dog-scout is a production-minded Python backend prototype that:

1. Pulls new token/pair data (Dexscreener or built-in mock data)
2. Applies hard risk filters
3. Computes rule score (0-100) and optional LLM narrative score
4. Merges weighted score (`RULE_WEIGHT` + `LLM_WEIGHT`) with safe fallback
5. Selects TopN with cooldown dedup
6. Emits initial alerts and 5m/15m recheck summary alerts
7. Persists raw pairs/signals/alerts/recheck jobs/results in SQLite

## Project Layout

- `dog_scout/clients/dexscreener.py`: market data client
- `dog_scout/filters.py`: hard filter logic
- `dog_scout/scoring.py`: rule scoring + weighted merge
- `dog_scout/analyzer.py`: pluggable LLM analyzers (`MockAnalyzer`, `DeepSeekAnalyzer`)
- `dog_scout/recheck.py`: recheck status transition logic
- `dog_scout/selector.py`: TopN + dedup
- `dog_scout/notifier.py`: Telegram notifier + message formatting
- `dog_scout/pipeline.py`: scan + recheck orchestration
- `dog_scout/storage.py`: SQLite persistence + migration application
- `dog_scout/db/migrations/`: schema migrations
- `tests/`: unit tests

## Setup

```bash
cd /home/laoye/.openclaw/workspace/dog-scout
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

## Initialize DB

```bash
python scripts/init_db.py
```

## Run

Single scan (dry-run):

```bash
python -m dog_scout.runner --mode once --dry-run
```

Single scan with deterministic mock market data:

```bash
python -m dog_scout.runner --mode once --dry-run --use-mock-data
```

Loop mode:

```bash
python -m dog_scout.runner --mode loop --interval 120 --dry-run
```

## LLM Analyzer

Supported providers:

- `deepseek`: OpenAI-compatible `/chat/completions`
- `mock`: deterministic analyzer for tests/dry-run demos

Main env options:

- `DOG_SCOUT_LLM_ENABLED` (default `false`)
- `DOG_SCOUT_LLM_PROVIDER` (default `deepseek`)
- `DOG_SCOUT_LLM_BASE_URL`
- `DOG_SCOUT_LLM_API_KEY`
- `DOG_SCOUT_LLM_MODEL` (default `deepseek-chat`)
- `DOG_SCOUT_LLM_TIMEOUT_SECONDS`
- `DOG_SCOUT_LLM_WEIGHT` (default `0.30`)
- `DOG_SCOUT_RULE_WEIGHT` (default `0.70`)

If analyzer request fails or times out, pipeline falls back to rule-only score automatically.

## Recheck Workflow

- Initial shortlisted token enqueues two recheck jobs: `+5m` and `+15m`.
- Each recheck refreshes market data, re-scores, and emits one concise summary alert.
- Recheck status is one of:
  - `IMPROVING`
  - `WEAKENING`
  - `INVALIDATED`
- Alerts include compact Chinese timeline line:
  - `首发分 -> 5m分 -> 15m分`

## Telegram Modes

- `DOG_SCOUT_DRY_RUN=true`: print messages to stdout (default)
- Real send mode requires:
  - `DOG_SCOUT_TELEGRAM_ENABLED=true`
  - `DOG_SCOUT_TELEGRAM_BOT_TOKEN=...`
  - `DOG_SCOUT_TELEGRAM_CHAT_ID=...`

## DB Tables

- `pairs_raw`
- `signals`
- `alerts`
- `trade_feedback`
- `recheck_jobs`
- `recheck_results`

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## Notes

- Analyzer and market API failures are non-fatal and logged.
- Dry-run behavior stays intact for both initial and recheck alerts.
- Existing scoring/dedup flow is preserved and remains backward compatible.
