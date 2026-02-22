from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(slots=True)
class PairSnapshot:
    chain_id: str
    pair_address: str
    dex_id: str
    base_token_address: str
    base_token_symbol: str
    quote_token_symbol: str
    price_usd: float
    liquidity_usd: float
    volume_h24: float
    txns_h1_buys: int
    txns_h1_sells: int
    price_change_h1: float | None
    price_change_h24: float | None
    pair_created_at: datetime | None
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskAssessment:
    is_honeypot: bool
    risk_flags: list[str]
    holders: int | None = None
    top10_concentration: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class FilterOutcome:
    passed: bool
    reasons: list[str]
    skipped_checks: list[str]


@dataclass(slots=True)
class ScoreBreakdown:
    liquidity_score: float
    txn_activity_score: float
    momentum_score: float
    final_score: float
    rule_score: float | None = None
    llm_score: float | None = None
    llm_confidence: float | None = None
    llm_provider: str | None = None
    llm_model: str | None = None
    llm_risk_comment: str | None = None
    llm_action_hint: str | None = None
    llm_reasons: list[str] = field(default_factory=list)
    llm_failed: bool = False


@dataclass(slots=True)
class Candidate:
    pair: PairSnapshot
    risk: RiskAssessment
    filter_outcome: FilterOutcome
    score: ScoreBreakdown
    pair_raw_id: int | None = None
    signal_id: int | None = None


@dataclass(slots=True)
class RecheckJob:
    id: int
    source_alert_id: int
    source_signal_id: int | None
    chain_id: str
    pair_address: str
    token_address: str
    token_symbol: str
    scheduled_minutes: int
    due_at: datetime
    status: str
    attempts: int


@dataclass(slots=True)
class ScoreTimeline:
    initial_score: float
    score_5m: float | None = None
    score_15m: float | None = None
