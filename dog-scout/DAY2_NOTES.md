# DAY2 Notes

## Scope Delivered

Day-2 features implemented for `dog-scout`:

- Pluggable LLM analyzer (`MockAnalyzer`, `DeepSeekAnalyzer`)
- Weighted score merge with graceful rule-only fallback on analyzer failure/timeout
- 5m/15m recheck scheduler + persistence + status alerts
- Compact Chinese score timeline line in alerts (`首发分 -> 5m分 -> 15m分`)
- Unit tests for fallback/merge/recheck transitions
- Docs and env updates

## Changed Files

- `dog_scout/analyzer.py`
- `dog_scout/recheck.py`
- `dog_scout/config.py`
- `dog_scout/models.py`
- `dog_scout/scoring.py`
- `dog_scout/pipeline.py`
- `dog_scout/storage.py`
- `dog_scout/notifier.py`
- `dog_scout/runner.py`
- `dog_scout/__init__.py`
- `dog_scout/db/migrations/002_day2_llm_recheck.sql`
- `tests/test_day2_features.py`
- `tests/test_scoring.py`
- `tests/test_filters.py`
- `README.md`
- `.env.example`
- `TODO.md`

## Validation Commands and Results

### 1) Unit tests

Command:

```bash
python3 -m unittest discover -s tests -v
```

Result:

- `Ran 9 tests in 0.371s`
- `OK`

### 2) Dry-run with mock LLM analyzer path + recheck outputs

Commands used:

```bash
DB_PATH="/tmp/dog_scout_day2_mock_<ts>.db"
DOG_SCOUT_DB_PATH="$DB_PATH" \
DOG_SCOUT_DRY_RUN=true \
DOG_SCOUT_USE_MOCK_DATA=true \
DOG_SCOUT_LLM_ENABLED=true \
DOG_SCOUT_LLM_PROVIDER=mock \
DOG_SCOUT_LLM_WEIGHT=0.30 \
DOG_SCOUT_RULE_WEIGHT=0.70 \
python3 -m dog_scout.runner --mode once --dry-run --use-mock-data

# force due jobs for demo
python3 - <<'PY'
import sqlite3
conn = sqlite3.connect("/tmp/dog_scout_day2_mock_<ts>.db")
conn.execute("UPDATE recheck_jobs SET due_at='2000-01-01 00:00:00' WHERE status='pending'")
conn.commit()
conn.close()
PY

DOG_SCOUT_DB_PATH="$DB_PATH" \
DOG_SCOUT_DRY_RUN=true \
DOG_SCOUT_USE_MOCK_DATA=true \
DOG_SCOUT_LLM_ENABLED=true \
DOG_SCOUT_LLM_PROVIDER=mock \
python3 -m dog_scout.runner --mode once --dry-run --use-mock-data
```

Sample output excerpts:

```text
scan complete | fetched=6 passed=5 selected=5 rechecked=0
🎯 土狗雷达 Top1 | 综合分 95.70/100
首发分 -> 5m分 -> 15m分：95.10 -> -- -> --

scan complete | fetched=6 passed=5 selected=0 rechecked=10
🔁 Recheck | DOGA | IMPROVING
首发分 -> 5m分 -> 15m分：95.50 -> 96.40 -> --
🔁 Recheck | DOGB | WEAKENING
首发分 -> 5m分 -> 15m分：95.70 -> 89.27 -> --
🔁 Recheck | DOGC | INVALIDATED
首发分 -> 5m分 -> 15m分：36.50 -> 42.06 -> 14.85
```

### 3) Dry-run with LLM disabled fallback

Commands used:

```bash
DB_PATH="/tmp/dog_scout_day2_nollm_<ts>.db"
DOG_SCOUT_DB_PATH="$DB_PATH" \
DOG_SCOUT_DRY_RUN=true \
DOG_SCOUT_USE_MOCK_DATA=true \
DOG_SCOUT_LLM_ENABLED=false \
python3 -m dog_scout.runner --mode once --dry-run --use-mock-data
```

Verification query:

```sql
SELECT final_score, rule_score, llm_score, llm_confidence, llm_failed
FROM signals
ORDER BY id DESC
LIMIT 1;
```

Sample query result:

```text
{'final_score': 45.1, 'rule_score': 45.1, 'llm_score': None, 'llm_confidence': None, 'llm_failed': 0}
```

This confirms rule-only fallback behavior when LLM is disabled.
