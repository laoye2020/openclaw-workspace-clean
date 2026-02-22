from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from dog_scout.models import RiskAssessment


class RiskProvider(Protocol):
    def assess_token(self, token_address: str, chain_id: str) -> RiskAssessment:
        ...


@dataclass(slots=True)
class MockRiskProvider:
    denylist_tokens: set[str]

    def assess_token(self, token_address: str, chain_id: str) -> RiskAssessment:
        token_lc = token_address.lower()
        flags: list[str] = []
        is_honeypot = False

        if token_lc in self.denylist_tokens:
            flags.append("denylisted_token")
            is_honeypot = True

        # Mock extension point: callers can replace this provider with a real one.
        return RiskAssessment(
            is_honeypot=is_honeypot,
            risk_flags=flags,
            holders=None,
            top10_concentration=None,
            metadata={"provider": "mock", "chain_id": chain_id},
        )
