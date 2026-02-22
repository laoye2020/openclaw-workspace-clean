from __future__ import annotations

import logging
from dataclasses import dataclass, replace
from datetime import datetime, timezone

from dog_scout.analyzer import (
    Analyzer,
    AnalyzerError,
    AnalyzerInput,
    DeepSeekAnalyzer,
    MockAnalyzer,
    build_market_snapshot,
)
from dog_scout.clients.dexscreener import DexscreenerClient
from dog_scout.config import Settings
from dog_scout.filters import apply_hard_filters
from dog_scout.models import Candidate, PairSnapshot, RecheckJob, ScoreBreakdown, ScoreTimeline
from dog_scout.notifier import (
    TelegramNotifier,
    format_recheck_summary_message,
    format_telegram_message,
)
from dog_scout.recheck import classify_recheck_status
from dog_scout.risk import MockRiskProvider, RiskProvider
from dog_scout.scoring import merge_with_analyzer, score_pair
from dog_scout.selector import select_top_candidates
from dog_scout.storage import Database

logger = logging.getLogger(__name__)

RECHECK_MINUTES = (5, 15)


@dataclass(slots=True)
class ScanResult:
    fetched_pairs: int
    passed_filters: int
    selected: int
    rechecked: int
    messages: list[str]


class ScoutPipeline:
    def __init__(
        self,
        settings: Settings,
        db: Database,
        client: DexscreenerClient | None = None,
        risk_provider: RiskProvider | None = None,
        notifier: TelegramNotifier | None = None,
        analyzer: Analyzer | None = None,
    ) -> None:
        self.settings = settings
        self.db = db
        self.client = client or DexscreenerClient(timeout_seconds=settings.request_timeout_seconds)
        self.risk_provider = risk_provider or MockRiskProvider(
            denylist_tokens=settings.denylist_tokens,
        )
        self.notifier = notifier or TelegramNotifier(settings=settings)
        self.analyzer = analyzer if analyzer is not None else self._build_default_analyzer()

    def run_once(self) -> ScanResult:
        recheck_messages = self._process_due_rechecks()

        pairs = self._fetch_pairs()
        if not pairs:
            logger.info("No pairs fetched this cycle")
            return ScanResult(
                fetched_pairs=0,
                passed_filters=0,
                selected=0,
                rechecked=len(recheck_messages),
                messages=recheck_messages,
            )

        candidates: list[Candidate] = []
        for pair in pairs:
            pair_raw_id = self.db.insert_pair_raw(pair)
            risk = self.risk_provider.assess_token(pair.base_token_address, pair.chain_id)
            filter_outcome = apply_hard_filters(pair, risk, self.settings)
            score = self._score_with_optional_analyzer(pair=pair, risk_flags=risk.risk_flags)
            signal_id = self.db.insert_signal(pair_raw_id, pair, risk, filter_outcome, score)

            if filter_outcome.passed:
                candidates.append(
                    Candidate(
                        pair=pair,
                        risk=risk,
                        filter_outcome=filter_outcome,
                        score=score,
                        pair_raw_id=pair_raw_id,
                        signal_id=signal_id,
                    )
                )

        selected = select_top_candidates(
            candidates=candidates,
            top_n=self.settings.top_n,
            cooldown_minutes=self.settings.dedup_cooldown_minutes,
            dedup_store=self.db,
        )

        initial_messages: list[str] = []
        for rank, candidate in enumerate(selected, start=1):
            message = format_telegram_message(rank=rank, candidate=candidate)
            result = self.notifier.send_message(message)
            alert_id = self.db.insert_alert(
                candidate=candidate,
                message=message,
                dry_run=self.settings.dry_run,
                status=result.status,
                sent=result.sent,
            )
            self.db.enqueue_recheck_jobs(
                candidate=candidate,
                source_alert_id=alert_id,
                scheduled_minutes=RECHECK_MINUTES,
            )
            initial_messages.append(message)

        messages = recheck_messages + initial_messages
        logger.info(
            "scan complete | fetched=%s passed=%s selected=%s rechecked=%s timestamp=%s",
            len(pairs),
            len(candidates),
            len(selected),
            len(recheck_messages),
            datetime.now(timezone.utc).isoformat(),
        )

        return ScanResult(
            fetched_pairs=len(pairs),
            passed_filters=len(candidates),
            selected=len(selected),
            rechecked=len(recheck_messages),
            messages=messages,
        )

    def _build_default_analyzer(self) -> Analyzer | None:
        if not self.settings.llm_enabled:
            return None
        provider = self.settings.llm_provider.lower()
        if provider == "mock":
            return MockAnalyzer()
        if provider == "deepseek":
            try:
                return DeepSeekAnalyzer(
                    base_url=self.settings.llm_base_url,
                    api_key=self.settings.llm_api_key,
                    model=self.settings.llm_model,
                    timeout_seconds=self.settings.llm_timeout_seconds,
                )
            except AnalyzerError as exc:
                logger.warning("LLM analyzer unavailable, fallback to rule-only: %s", exc)
                return None

        logger.warning("Unsupported LLM provider '%s', fallback to rule-only", provider)
        return None

    def _score_with_optional_analyzer(self, pair: PairSnapshot, risk_flags: list[str]) -> ScoreBreakdown:
        rule_breakdown = score_pair(pair, self.settings)
        provider_name = self.settings.llm_provider.lower()
        model_name = self.settings.llm_model

        if not self.settings.llm_enabled or self.analyzer is None:
            return merge_with_analyzer(
                rule_breakdown=rule_breakdown,
                analyzer_output=None,
                settings=self.settings,
                analyzer_provider=provider_name,
                analyzer_model=model_name,
                analyzer_failed=bool(self.settings.llm_enabled and self.analyzer is None),
            )

        txns_h1 = max(pair.txns_h1_buys, 0) + max(pair.txns_h1_sells, 0)
        analyzer_input = AnalyzerInput(
            chain_id=pair.chain_id,
            token_address=pair.base_token_address,
            token_symbol=pair.base_token_symbol,
            pair_address=pair.pair_address,
            dex_id=pair.dex_id,
            rule_score=rule_breakdown.final_score,
            liquidity_usd=pair.liquidity_usd,
            txns_h1=txns_h1,
            price_change_h1=pair.price_change_h1,
            price_change_h24=pair.price_change_h24,
            volume_h24=pair.volume_h24,
            risk_flags=risk_flags,
            market_snapshot=build_market_snapshot(
                liquidity_usd=pair.liquidity_usd,
                volume_h24=pair.volume_h24,
                txns_h1=txns_h1,
                price_change_h1=pair.price_change_h1,
                price_change_h24=pair.price_change_h24,
                dex_id=pair.dex_id,
            ),
        )

        try:
            analyzer_output = self.analyzer.analyze(analyzer_input)
        except AnalyzerError as exc:
            logger.warning("Analyzer failed for %s: %s", pair.base_token_address, exc)
            return merge_with_analyzer(
                rule_breakdown=rule_breakdown,
                analyzer_output=None,
                settings=self.settings,
                analyzer_provider=getattr(self.analyzer, "provider", provider_name),
                analyzer_model=getattr(self.analyzer, "model", model_name),
                analyzer_failed=True,
            )

        return merge_with_analyzer(
            rule_breakdown=rule_breakdown,
            analyzer_output=analyzer_output,
            settings=self.settings,
            analyzer_provider=getattr(self.analyzer, "provider", provider_name),
            analyzer_model=getattr(self.analyzer, "model", model_name),
            analyzer_failed=False,
        )

    def _process_due_rechecks(self) -> list[str]:
        jobs = self.db.claim_due_recheck_jobs(limit=self.settings.recheck_batch_size)
        if not jobs:
            return []

        messages: list[str] = []
        for job in jobs:
            try:
                maybe_message = self._run_single_recheck(job)
                if maybe_message:
                    messages.append(maybe_message)
                self.db.mark_recheck_job_done(job.id)
            except Exception as exc:  # noqa: BLE001 - keep pipeline resilient
                logger.exception("Recheck job failed | job_id=%s", job.id)
                self.db.mark_recheck_job_failed(job.id, str(exc))
        return messages

    def _run_single_recheck(self, job: RecheckJob) -> str | None:
        pair = self._refresh_pair_for_recheck(job)
        if pair is None:
            raise RuntimeError(f"No market data for recheck job {job.id}")

        pair_raw_id = self.db.insert_pair_raw(pair)
        risk = self.risk_provider.assess_token(pair.base_token_address, pair.chain_id)
        filter_outcome = apply_hard_filters(pair, risk, self.settings)
        score = self._score_with_optional_analyzer(pair=pair, risk_flags=risk.risk_flags)
        signal_id = self.db.insert_signal(pair_raw_id, pair, risk, filter_outcome, score)
        candidate = Candidate(
            pair=pair,
            risk=risk,
            filter_outcome=filter_outcome,
            score=score,
            pair_raw_id=pair_raw_id,
            signal_id=signal_id,
        )

        initial_score = self.db.get_alert_score(job.source_alert_id)
        if initial_score is None:
            raise RuntimeError(f"Missing source alert {job.source_alert_id}")

        previous_score = self.db.get_previous_recheck_score(
            source_alert_id=job.source_alert_id,
            scheduled_minutes=job.scheduled_minutes,
        )
        status = classify_recheck_status(
            passed_filters=filter_outcome.passed,
            initial_score=initial_score,
            previous_score=previous_score,
            current_score=score.final_score,
        )

        timeline = self.db.get_timeline_for_alert(job.source_alert_id) or ScoreTimeline(
            initial_score=initial_score
        )
        if job.scheduled_minutes == 5:
            timeline.score_5m = score.final_score
        elif job.scheduled_minutes == 15:
            timeline.score_15m = score.final_score

        base_score = previous_score if previous_score is not None else initial_score
        delta_from_initial = round(score.final_score - initial_score, 2)
        delta_from_previous = round(score.final_score - base_score, 2)

        message = format_recheck_summary_message(
            candidate=candidate,
            status=status,
            timeline=timeline,
            delta_from_initial=delta_from_initial,
            delta_from_previous=delta_from_previous,
        )
        notify_result = self.notifier.send_message(message)
        self.db.insert_alert(
            candidate=candidate,
            message=message,
            dry_run=self.settings.dry_run,
            status=notify_result.status,
            sent=notify_result.sent,
        )
        self.db.insert_recheck_result(
            job=job,
            candidate=candidate,
            status=status,
            timeline=timeline,
            delta_from_initial=delta_from_initial,
            delta_from_previous=delta_from_previous,
            message=message,
        )
        return message

    def _refresh_pair_for_recheck(self, job: RecheckJob) -> PairSnapshot | None:
        if self.settings.use_mock_data:
            return self._mock_recheck_pair(job)

        pairs = self.client.fetch_token_pairs(chain_id=job.chain_id, token_address=job.token_address)
        if not pairs:
            return None

        same_pair = [pair for pair in pairs if pair.pair_address.lower() == job.pair_address.lower()]
        candidates = same_pair or pairs
        return sorted(
            candidates,
            key=lambda item: item.pair_created_at or datetime.min.replace(tzinfo=timezone.utc),
            reverse=True,
        )[0]

    def _mock_recheck_pair(self, job: RecheckJob) -> PairSnapshot | None:
        base_pair = None
        for pair in _mock_pairs(job.chain_id):
            if pair.base_token_address.lower() == job.token_address.lower():
                base_pair = pair
                break
        if base_pair is None:
            return None

        token_suffix = job.token_address.lower()[-1]
        is_improving = token_suffix in {"a", "d"}
        is_invalidating = token_suffix in {"c", "f"}
        multiplier = 1.0 + (0.06 * (job.scheduled_minutes // 5))

        pair = replace(base_pair)
        if is_improving:
            pair.liquidity_usd = round(base_pair.liquidity_usd * (1.0 + 0.08 * (job.scheduled_minutes // 5)), 2)
            pair.txns_h1_buys = int(base_pair.txns_h1_buys * multiplier)
            pair.txns_h1_sells = int(base_pair.txns_h1_sells * multiplier)
            pair.price_change_h1 = (base_pair.price_change_h1 or 0.0) + (2.0 * (job.scheduled_minutes // 5))
        elif is_invalidating and job.scheduled_minutes >= 15:
            pair.liquidity_usd = min(base_pair.liquidity_usd * 0.35, self.settings.min_liquidity_usd * 0.4)
            pair.txns_h1_buys = int(base_pair.txns_h1_buys * 0.55)
            pair.txns_h1_sells = int(base_pair.txns_h1_sells * 0.55)
            pair.price_change_h1 = -72.0
        else:
            pair.liquidity_usd = round(base_pair.liquidity_usd * (1.0 - 0.07 * (job.scheduled_minutes // 5)), 2)
            pair.txns_h1_buys = int(base_pair.txns_h1_buys * (1.0 - 0.11 * (job.scheduled_minutes // 5)))
            pair.txns_h1_sells = int(base_pair.txns_h1_sells * (1.0 - 0.11 * (job.scheduled_minutes // 5)))
            pair.price_change_h1 = (base_pair.price_change_h1 or 0.0) - (3.0 * (job.scheduled_minutes // 5))

        pair.raw = dict(base_pair.raw)
        pair.raw["mock_recheck_minutes"] = job.scheduled_minutes
        return pair

    def _fetch_pairs(self) -> list[PairSnapshot]:
        if self.settings.use_mock_data:
            return _mock_pairs(self.settings.chain_id)
        return self.client.fetch_new_pairs(
            chain_id=self.settings.chain_id,
            max_tokens=self.settings.max_new_tokens,
        )


def _mock_pairs(chain_id: str) -> list[PairSnapshot]:
    now = datetime.now(timezone.utc)
    return [
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairA",
            dex_id="uniswap",
            base_token_address="0xtokenA",
            base_token_symbol="DOGA",
            quote_token_symbol="WETH",
            price_usd=0.00042,
            liquidity_usd=120000,
            volume_h24=350000,
            txns_h1_buys=64,
            txns_h1_sells=39,
            price_change_h1=18.0,
            price_change_h24=47.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairB",
            dex_id="aerodrome",
            base_token_address="0xtokenB",
            base_token_symbol="DOGB",
            quote_token_symbol="USDC",
            price_usd=0.0018,
            liquidity_usd=81000,
            volume_h24=162000,
            txns_h1_buys=45,
            txns_h1_sells=41,
            price_change_h1=9.0,
            price_change_h24=21.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairC",
            dex_id="uniswap",
            base_token_address="0xtokenC",
            base_token_symbol="DOGC",
            quote_token_symbol="WETH",
            price_usd=0.00009,
            liquidity_usd=34000,
            volume_h24=98000,
            txns_h1_buys=31,
            txns_h1_sells=27,
            price_change_h1=82.0,
            price_change_h24=89.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairD",
            dex_id="sushiswap",
            base_token_address="0xtokenD",
            base_token_symbol="DOGD",
            quote_token_symbol="WETH",
            price_usd=0.00014,
            liquidity_usd=26000,
            volume_h24=62000,
            txns_h1_buys=14,
            txns_h1_sells=12,
            price_change_h1=-8.0,
            price_change_h24=4.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairE",
            dex_id="aerodrome",
            base_token_address="0xtokenE",
            base_token_symbol="DOGE2",
            quote_token_symbol="USDC",
            price_usd=0.00073,
            liquidity_usd=53000,
            volume_h24=91000,
            txns_h1_buys=26,
            txns_h1_sells=23,
            price_change_h1=28.0,
            price_change_h24=44.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
        PairSnapshot(
            chain_id=chain_id,
            pair_address="0xpairF",
            dex_id="uniswap",
            base_token_address="0xtokenF",
            base_token_symbol="DOGF",
            quote_token_symbol="WETH",
            price_usd=0.00003,
            liquidity_usd=15000,
            volume_h24=40000,
            txns_h1_buys=19,
            txns_h1_sells=17,
            price_change_h1=11.0,
            price_change_h24=19.0,
            pair_created_at=now,
            raw={"source": "mock"},
        ),
    ]
