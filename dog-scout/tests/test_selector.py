import unittest

from dog_scout.models import Candidate, FilterOutcome, PairSnapshot, RiskAssessment, ScoreBreakdown
from dog_scout.selector import select_top_candidates


class FakeDedupStore:
    def __init__(self, blocked: set[str]) -> None:
        self.blocked = blocked

    def has_recent_alert(self, token_address: str, pair_address: str, cooldown_minutes: int) -> bool:
        return token_address in self.blocked or pair_address in self.blocked


def build_candidate(symbol: str, token: str, pair: str, score: float) -> Candidate:
    pair_snapshot = PairSnapshot(
        chain_id="base",
        pair_address=pair,
        dex_id="uniswap",
        base_token_address=token,
        base_token_symbol=symbol,
        quote_token_symbol="WETH",
        price_usd=0.001,
        liquidity_usd=50_000,
        volume_h24=100_000,
        txns_h1_buys=20,
        txns_h1_sells=10,
        price_change_h1=8.0,
        price_change_h24=17.0,
        pair_created_at=None,
        raw={},
    )
    return Candidate(
        pair=pair_snapshot,
        risk=RiskAssessment(is_honeypot=False, risk_flags=[]),
        filter_outcome=FilterOutcome(passed=True, reasons=[], skipped_checks=[]),
        score=ScoreBreakdown(30.0, 20.0, 15.0, score),
    )


class SelectorTests(unittest.TestCase):
    def test_selector_applies_ranking_and_dedup(self) -> None:
        candidates = [
            build_candidate("A", "0xtA", "0xpA", 91.0),
            build_candidate("B", "0xtB", "0xpB", 88.0),
            build_candidate("C", "0xtC", "0xpC", 85.0),
        ]
        dedup = FakeDedupStore(blocked={"0xtB"})

        selected = select_top_candidates(
            candidates=candidates,
            top_n=2,
            cooldown_minutes=30,
            dedup_store=dedup,
        )

        self.assertEqual(len(selected), 2)
        self.assertEqual(selected[0].pair.base_token_symbol, "A")
        self.assertEqual(selected[1].pair.base_token_symbol, "C")


if __name__ == "__main__":
    unittest.main()
