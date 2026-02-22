from __future__ import annotations

from dataclasses import replace

from dog_scout.analyzer import AnalyzerOutput
from dog_scout.config import Settings
from dog_scout.models import PairSnapshot, ScoreBreakdown


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def score_pair(pair: PairSnapshot, settings: Settings) -> ScoreBreakdown:
    # 0..40
    liquidity_target = max(settings.min_liquidity_usd * 4.0, 1.0)
    liquidity_score = _clamp((pair.liquidity_usd / liquidity_target) * 40.0, 0.0, 40.0)

    # 0..35
    txns_h1 = max(pair.txns_h1_buys, 0) + max(pair.txns_h1_sells, 0)
    txn_target = max(settings.txn_target_h1, 1)
    txn_activity_score = _clamp((txns_h1 / txn_target) * 35.0, 0.0, 35.0)

    # 0..25
    momentum_score = _momentum_score(
        price_change_h1=pair.price_change_h1,
        price_change_h24=pair.price_change_h24,
        blowoff_threshold=settings.momentum_blowoff_threshold,
    )

    final_score = _clamp(liquidity_score + txn_activity_score + momentum_score, 0.0, 100.0)

    return ScoreBreakdown(
        liquidity_score=round(liquidity_score, 2),
        txn_activity_score=round(txn_activity_score, 2),
        momentum_score=round(momentum_score, 2),
        final_score=round(final_score, 2),
        rule_score=round(final_score, 2),
    )


def merge_with_analyzer(
    rule_breakdown: ScoreBreakdown,
    analyzer_output: AnalyzerOutput | None,
    settings: Settings,
    analyzer_provider: str | None = None,
    analyzer_model: str | None = None,
    analyzer_failed: bool = False,
) -> ScoreBreakdown:
    rule_score = rule_breakdown.rule_score if rule_breakdown.rule_score is not None else rule_breakdown.final_score
    rule_score = _clamp(rule_score, 0.0, 100.0)

    if analyzer_output is None:
        return replace(
            rule_breakdown,
            final_score=round(rule_score, 2),
            rule_score=round(rule_score, 2),
            llm_score=None,
            llm_confidence=None,
            llm_provider=analyzer_provider,
            llm_model=analyzer_model,
            llm_risk_comment=None,
            llm_action_hint=None,
            llm_reasons=[],
            llm_failed=analyzer_failed,
        )

    rule_weight, llm_weight = _normalized_weights(settings.rule_weight, settings.llm_weight)
    merged = _clamp((rule_score * rule_weight) + (analyzer_output.narrative_score * llm_weight), 0.0, 100.0)
    return replace(
        rule_breakdown,
        final_score=round(merged, 2),
        rule_score=round(rule_score, 2),
        llm_score=round(analyzer_output.narrative_score, 2),
        llm_confidence=round(analyzer_output.confidence, 2),
        llm_provider=analyzer_provider,
        llm_model=analyzer_model,
        llm_risk_comment=analyzer_output.risk_comment,
        llm_action_hint=analyzer_output.action_hint,
        llm_reasons=list(analyzer_output.reasons),
        llm_failed=False,
    )


def _momentum_score(
    price_change_h1: float | None,
    price_change_h24: float | None,
    blowoff_threshold: float,
) -> float:
    if price_change_h1 is None:
        return 12.0

    change = price_change_h1
    abs_change = abs(change)

    if change < -60:
        score = 1.5
    elif abs_change <= 12:
        score = 25.0
    elif abs_change <= 25:
        score = 22.0
    elif abs_change <= 45:
        score = 17.0
    elif abs_change <= blowoff_threshold:
        score = 12.0
    else:
        score = 4.0

    # Sanity penalty: sharp 1h move nearly equals full 24h move.
    if (
        price_change_h24 is not None
        and change > 20
        and price_change_h24 > 0
        and change >= 0.8 * price_change_h24
    ):
        score -= 3.0

    return _clamp(score, 0.0, 25.0)


def _normalized_weights(rule_weight: float, llm_weight: float) -> tuple[float, float]:
    safe_rule = max(rule_weight, 0.0)
    safe_llm = max(llm_weight, 0.0)
    total = safe_rule + safe_llm
    if total <= 0:
        return (1.0, 0.0)
    return (safe_rule / total, safe_llm / total)
