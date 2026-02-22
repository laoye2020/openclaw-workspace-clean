from __future__ import annotations

IMPROVING = "IMPROVING"
WEAKENING = "WEAKENING"
INVALIDATED = "INVALIDATED"


def classify_recheck_status(
    passed_filters: bool,
    initial_score: float,
    previous_score: float | None,
    current_score: float,
) -> str:
    if not passed_filters:
        return INVALIDATED

    reference = previous_score if previous_score is not None else initial_score
    delta = current_score - reference
    if delta >= 2.0:
        return IMPROVING
    if delta <= -2.0:
        return WEAKENING
    return IMPROVING if current_score >= initial_score else WEAKENING
