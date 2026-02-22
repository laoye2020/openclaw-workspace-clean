import unittest
from pathlib import Path

from dog_scout.config import Settings
from dog_scout.filters import apply_hard_filters
from dog_scout.models import PairSnapshot, RiskAssessment


def build_settings() -> Settings:
    return Settings(
        db_path=Path("./test.db"),
        chain_id="base",
        loop_interval_seconds=120,
        top_n=5,
        dedup_cooldown_minutes=30,
        dry_run=True,
        use_mock_data=True,
        request_timeout_seconds=10,
        max_new_tokens=20,
        min_liquidity_usd=20_000,
        min_holders=200,
        max_top10_concentration=0.45,
        denylist_tokens=set(),
        txn_target_h1=100,
        momentum_blowoff_threshold=80.0,
        llm_enabled=False,
        llm_provider="deepseek",
        llm_base_url="https://api.deepseek.com/v1",
        llm_api_key="",
        llm_model="deepseek-chat",
        llm_timeout_seconds=12,
        llm_weight=0.30,
        rule_weight=0.70,
        recheck_batch_size=20,
        telegram_enabled=False,
        telegram_bot_token="",
        telegram_chat_id="",
    )


def build_pair(liquidity: float = 30_000) -> PairSnapshot:
    return PairSnapshot(
        chain_id="base",
        pair_address="0xpair",
        dex_id="uniswap",
        base_token_address="0xtoken",
        base_token_symbol="DOG",
        quote_token_symbol="WETH",
        price_usd=0.001,
        liquidity_usd=liquidity,
        volume_h24=100_000,
        txns_h1_buys=10,
        txns_h1_sells=11,
        price_change_h1=12.0,
        price_change_h24=26.0,
        pair_created_at=None,
        raw={},
    )


class FilterTests(unittest.TestCase):
    def test_filter_fails_when_liquidity_below_threshold(self) -> None:
        settings = build_settings()
        pair = build_pair(liquidity=5_000)
        risk = RiskAssessment(is_honeypot=False, risk_flags=[])

        outcome = apply_hard_filters(pair, risk, settings)

        self.assertFalse(outcome.passed)
        self.assertTrue(any("liquidity_below_threshold" in item for item in outcome.reasons))

    def test_filter_skips_unavailable_holders_and_top10(self) -> None:
        settings = build_settings()
        pair = build_pair(liquidity=30_000)
        risk = RiskAssessment(
            is_honeypot=False,
            risk_flags=[],
            holders=None,
            top10_concentration=None,
        )

        outcome = apply_hard_filters(pair, risk, settings)

        self.assertTrue(outcome.passed)
        self.assertIn("holders_unavailable", outcome.skipped_checks)
        self.assertIn("top10_concentration_unavailable", outcome.skipped_checks)

    def test_filter_fails_when_risk_provider_blocks(self) -> None:
        settings = build_settings()
        pair = build_pair(liquidity=30_000)
        risk = RiskAssessment(is_honeypot=True, risk_flags=["denylisted_token"])

        outcome = apply_hard_filters(pair, risk, settings)

        self.assertFalse(outcome.passed)
        self.assertIn("risk_provider_block", outcome.reasons)


if __name__ == "__main__":
    unittest.main()
