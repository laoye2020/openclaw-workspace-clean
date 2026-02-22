import unittest
from pathlib import Path

from dog_scout.config import Settings
from dog_scout.models import PairSnapshot
from dog_scout.scoring import score_pair


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


def build_pair(
    liquidity: float,
    buys: int,
    sells: int,
    h1: float | None,
    h24: float | None,
) -> PairSnapshot:
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
        txns_h1_buys=buys,
        txns_h1_sells=sells,
        price_change_h1=h1,
        price_change_h24=h24,
        pair_created_at=None,
        raw={},
    )


class ScoringTests(unittest.TestCase):
    def test_scoring_prefers_healthier_liquidity_and_activity(self) -> None:
        settings = build_settings()
        weak = build_pair(liquidity=25_000, buys=5, sells=7, h1=10, h24=22)
        strong = build_pair(liquidity=120_000, buys=70, sells=50, h1=12, h24=30)

        weak_score = score_pair(weak, settings)
        strong_score = score_pair(strong, settings)

        self.assertGreater(strong_score.final_score, weak_score.final_score)
        self.assertGreaterEqual(strong_score.final_score, 0)
        self.assertLessEqual(strong_score.final_score, 100)

    def test_scoring_penalizes_blowoff_momentum(self) -> None:
        settings = build_settings()
        sane = build_pair(liquidity=80_000, buys=55, sells=40, h1=14, h24=35)
        blowoff = build_pair(liquidity=80_000, buys=55, sells=40, h1=120, h24=130)

        sane_score = score_pair(sane, settings)
        blowoff_score = score_pair(blowoff, settings)

        self.assertGreater(sane_score.momentum_score, blowoff_score.momentum_score)
        self.assertGreater(sane_score.final_score, blowoff_score.final_score)


if __name__ == "__main__":
    unittest.main()
