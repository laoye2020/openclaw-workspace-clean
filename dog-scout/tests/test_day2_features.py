import sqlite3
import tempfile
import unittest
from pathlib import Path

from dog_scout.analyzer import AnalyzerError, AnalyzerOutput
from dog_scout.config import Settings
from dog_scout.models import ScoreBreakdown
from dog_scout.pipeline import ScoutPipeline
from dog_scout.recheck import INVALIDATED, IMPROVING, WEAKENING, classify_recheck_status
from dog_scout.scoring import merge_with_analyzer
from dog_scout.storage import Database


def build_settings(db_path: Path, llm_enabled: bool = True) -> Settings:
    return Settings(
        db_path=db_path,
        chain_id="base",
        loop_interval_seconds=120,
        top_n=3,
        dedup_cooldown_minutes=30,
        dry_run=True,
        use_mock_data=True,
        request_timeout_seconds=10,
        max_new_tokens=20,
        min_liquidity_usd=20_000,
        min_holders=100,
        max_top10_concentration=0.50,
        denylist_tokens=set(),
        txn_target_h1=100,
        momentum_blowoff_threshold=80.0,
        llm_enabled=llm_enabled,
        llm_provider="mock",
        llm_base_url="https://api.deepseek.com/v1",
        llm_api_key="",
        llm_model="deepseek-chat",
        llm_timeout_seconds=5,
        llm_weight=0.30,
        rule_weight=0.70,
        recheck_batch_size=20,
        telegram_enabled=False,
        telegram_bot_token="",
        telegram_chat_id="",
    )


class FailingAnalyzer:
    provider = "mock"
    model = "mock-v1"

    def analyze(self, payload):  # noqa: ANN001
        raise AnalyzerError("forced failure")


class Day2FeatureTests(unittest.TestCase):
    def test_weighted_merge_uses_configured_weights(self) -> None:
        settings = build_settings(Path("./tmp.db"))
        rule = ScoreBreakdown(
            liquidity_score=35.0,
            txn_activity_score=25.0,
            momentum_score=20.0,
            final_score=80.0,
            rule_score=80.0,
        )
        llm = AnalyzerOutput(
            narrative_score=50.0,
            risk_comment="ok",
            action_hint="wait",
            confidence=0.7,
            reasons=["test"],
        )

        merged = merge_with_analyzer(rule, llm, settings)

        self.assertAlmostEqual(merged.final_score, 71.0)
        self.assertEqual(merged.rule_score, 80.0)
        self.assertEqual(merged.llm_score, 50.0)

    def test_analyzer_fallback_keeps_rule_score(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "dog_scout.db"
            settings = build_settings(db_path=db_path, llm_enabled=True)
            db = Database(db_path)
            db.ensure_initialized()

            pipeline = ScoutPipeline(
                settings=settings,
                db=db,
                analyzer=FailingAnalyzer(),
            )
            result = pipeline.run_once()
            self.assertGreater(result.selected, 0)

            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            row = conn.execute(
                """
                SELECT final_score, rule_score, llm_failed
                FROM signals
                ORDER BY id DESC
                LIMIT 1
                """
            ).fetchone()
            conn.close()
            self.assertIsNotNone(row)
            self.assertAlmostEqual(float(row["final_score"]), float(row["rule_score"]), places=2)
            self.assertEqual(int(row["llm_failed"]), 1)

    def test_recheck_state_transitions(self) -> None:
        self.assertEqual(
            classify_recheck_status(
                passed_filters=True,
                initial_score=70.0,
                previous_score=72.0,
                current_score=76.0,
            ),
            IMPROVING,
        )
        self.assertEqual(
            classify_recheck_status(
                passed_filters=True,
                initial_score=70.0,
                previous_score=72.0,
                current_score=69.0,
            ),
            WEAKENING,
        )
        self.assertEqual(
            classify_recheck_status(
                passed_filters=False,
                initial_score=70.0,
                previous_score=72.0,
                current_score=88.0,
            ),
            INVALIDATED,
        )


if __name__ == "__main__":
    unittest.main()
