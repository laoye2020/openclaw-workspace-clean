from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _get_csv_set(name: str) -> set[str]:
    raw = os.getenv(name, "")
    values = {item.strip().lower() for item in raw.split(",") if item.strip()}
    return values


@dataclass(slots=True)
class Settings:
    db_path: Path
    chain_id: str
    loop_interval_seconds: int
    top_n: int
    dedup_cooldown_minutes: int
    dry_run: bool
    use_mock_data: bool

    request_timeout_seconds: int
    max_new_tokens: int

    min_liquidity_usd: float
    min_holders: int
    max_top10_concentration: float
    denylist_tokens: set[str]

    txn_target_h1: int
    momentum_blowoff_threshold: float

    llm_enabled: bool
    llm_provider: str
    llm_base_url: str
    llm_api_key: str
    llm_model: str
    llm_timeout_seconds: int
    llm_weight: float
    rule_weight: float

    recheck_batch_size: int

    telegram_enabled: bool
    telegram_bot_token: str
    telegram_chat_id: str

    @classmethod
    def from_env(cls) -> "Settings":
        db_path = Path(os.getenv("DOG_SCOUT_DB_PATH", "./dog_scout.db")).expanduser()
        return cls(
            db_path=db_path,
            chain_id=os.getenv("DOG_SCOUT_CHAIN_ID", "base").strip().lower(),
            loop_interval_seconds=_get_int("DOG_SCOUT_LOOP_INTERVAL_SECONDS", 120),
            top_n=_get_int("DOG_SCOUT_TOP_N", 5),
            dedup_cooldown_minutes=_get_int("DOG_SCOUT_DEDUP_COOLDOWN_MINUTES", 30),
            dry_run=_get_bool("DOG_SCOUT_DRY_RUN", True),
            use_mock_data=_get_bool("DOG_SCOUT_USE_MOCK_DATA", False),
            request_timeout_seconds=_get_int("DOG_SCOUT_REQUEST_TIMEOUT_SECONDS", 10),
            max_new_tokens=_get_int("DOG_SCOUT_MAX_NEW_TOKENS", 40),
            min_liquidity_usd=_get_float("DOG_SCOUT_MIN_LIQUIDITY_USD", 20000.0),
            min_holders=_get_int("DOG_SCOUT_MIN_HOLDERS", 100),
            max_top10_concentration=_get_float("DOG_SCOUT_MAX_TOP10_CONCENTRATION", 0.50),
            denylist_tokens=_get_csv_set("DOG_SCOUT_DENYLIST_TOKENS"),
            txn_target_h1=_get_int("DOG_SCOUT_TXN_TARGET_H1", 100),
            momentum_blowoff_threshold=_get_float("DOG_SCOUT_MOMENTUM_BLOWOFF_THRESHOLD", 80.0),
            llm_enabled=_get_bool("DOG_SCOUT_LLM_ENABLED", False),
            llm_provider=os.getenv("DOG_SCOUT_LLM_PROVIDER", "deepseek").strip().lower(),
            llm_base_url=os.getenv("DOG_SCOUT_LLM_BASE_URL", "https://api.deepseek.com/v1").strip(),
            llm_api_key=os.getenv("DOG_SCOUT_LLM_API_KEY", "").strip(),
            llm_model=os.getenv("DOG_SCOUT_LLM_MODEL", "deepseek-chat").strip(),
            llm_timeout_seconds=_get_int("DOG_SCOUT_LLM_TIMEOUT_SECONDS", 12),
            llm_weight=_get_float("DOG_SCOUT_LLM_WEIGHT", 0.30),
            rule_weight=_get_float("DOG_SCOUT_RULE_WEIGHT", 0.70),
            recheck_batch_size=_get_int("DOG_SCOUT_RECHECK_BATCH_SIZE", 20),
            telegram_enabled=_get_bool("DOG_SCOUT_TELEGRAM_ENABLED", False),
            telegram_bot_token=os.getenv("DOG_SCOUT_TELEGRAM_BOT_TOKEN", "").strip(),
            telegram_chat_id=os.getenv("DOG_SCOUT_TELEGRAM_CHAT_ID", "").strip(),
        )
