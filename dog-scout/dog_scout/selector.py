from __future__ import annotations

from typing import Protocol

from dog_scout.models import Candidate


class DedupStore(Protocol):
    def has_recent_alert(self, token_address: str, pair_address: str, cooldown_minutes: int) -> bool:
        ...


def select_top_candidates(
    candidates: list[Candidate],
    top_n: int,
    cooldown_minutes: int,
    dedup_store: DedupStore,
) -> list[Candidate]:
    selected: list[Candidate] = []
    sorted_candidates = sorted(
        candidates,
        key=lambda item: item.score.final_score,
        reverse=True,
    )

    for candidate in sorted_candidates:
        if len(selected) >= top_n:
            break
        if dedup_store.has_recent_alert(
            token_address=candidate.pair.base_token_address,
            pair_address=candidate.pair.pair_address,
            cooldown_minutes=cooldown_minutes,
        ):
            continue
        selected.append(candidate)

    return selected
