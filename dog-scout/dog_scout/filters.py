from __future__ import annotations

from dog_scout.config import Settings
from dog_scout.models import FilterOutcome, PairSnapshot, RiskAssessment


def apply_hard_filters(
    pair: PairSnapshot,
    risk: RiskAssessment,
    settings: Settings,
) -> FilterOutcome:
    reasons: list[str] = []
    skipped_checks: list[str] = []

    if pair.liquidity_usd < settings.min_liquidity_usd:
        reasons.append(
            f"liquidity_below_threshold:{pair.liquidity_usd:.2f}<{settings.min_liquidity_usd:.2f}"
        )

    if risk.holders is None:
        skipped_checks.append("holders_unavailable")
    elif risk.holders < settings.min_holders:
        reasons.append(f"holders_below_threshold:{risk.holders}<{settings.min_holders}")

    if risk.top10_concentration is None:
        skipped_checks.append("top10_concentration_unavailable")
    elif risk.top10_concentration > settings.max_top10_concentration:
        reasons.append(
            "top10_concentration_above_threshold:"
            f"{risk.top10_concentration:.4f}>{settings.max_top10_concentration:.4f}"
        )

    if risk.is_honeypot or any(flag in {"honeypot", "denylisted_token"} for flag in risk.risk_flags):
        reasons.append("risk_provider_block")

    return FilterOutcome(
        passed=not reasons,
        reasons=reasons,
        skipped_checks=skipped_checks,
    )
