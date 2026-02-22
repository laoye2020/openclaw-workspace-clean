from __future__ import annotations

import json
import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Iterator, Sequence

from dog_scout.models import (
    Candidate,
    FilterOutcome,
    PairSnapshot,
    RecheckJob,
    RiskAssessment,
    ScoreBreakdown,
    ScoreTimeline,
)

logger = logging.getLogger(__name__)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _to_sqlite_ts(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_sqlite_ts(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw)
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


class Database:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path

    @contextmanager
    def connect(self) -> Iterator[sqlite3.Connection]:
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def ensure_initialized(self) -> None:
        migrations_dir = Path(__file__).parent / "db" / "migrations"
        with self.connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS applied_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT NOT NULL UNIQUE,
                    applied_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            applied = {
                row["filename"]
                for row in conn.execute("SELECT filename FROM applied_migrations")
            }
            for migration in sorted(migrations_dir.glob("*.sql")):
                if migration.name in applied:
                    continue
                sql = migration.read_text(encoding="utf-8")
                conn.executescript(sql)
                conn.execute(
                    "INSERT INTO applied_migrations (filename) VALUES (?)",
                    (migration.name,),
                )
                logger.info("Applied migration %s", migration.name)

    def insert_pair_raw(self, pair: PairSnapshot) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO pairs_raw (
                    chain_id, pair_address, token_address, dex_id,
                    liquidity_usd, price_usd, volume_h24,
                    txns_h1_buys, txns_h1_sells,
                    pair_created_at, raw_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pair.chain_id,
                    pair.pair_address,
                    pair.base_token_address,
                    pair.dex_id,
                    pair.liquidity_usd,
                    pair.price_usd,
                    pair.volume_h24,
                    pair.txns_h1_buys,
                    pair.txns_h1_sells,
                    pair.pair_created_at.isoformat() if pair.pair_created_at else None,
                    json.dumps(pair.raw, ensure_ascii=True),
                ),
            )
            return int(cursor.lastrowid)

    def insert_signal(
        self,
        pair_raw_id: int,
        pair: PairSnapshot,
        risk: RiskAssessment,
        filter_outcome: FilterOutcome,
        score: ScoreBreakdown,
    ) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO signals (
                    pair_raw_id, chain_id, pair_address, token_address,
                    liquidity_score, txn_activity_score, momentum_score, final_score, rule_score,
                    llm_score, llm_confidence, llm_provider, llm_model,
                    passed_filters, filter_reasons, skipped_checks, risk_flags,
                    holders, top10_concentration,
                    llm_risk_comment, llm_action_hint, llm_reasons, llm_failed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    pair_raw_id,
                    pair.chain_id,
                    pair.pair_address,
                    pair.base_token_address,
                    score.liquidity_score,
                    score.txn_activity_score,
                    score.momentum_score,
                    score.final_score,
                    score.rule_score if score.rule_score is not None else score.final_score,
                    score.llm_score,
                    score.llm_confidence,
                    score.llm_provider,
                    score.llm_model,
                    int(filter_outcome.passed),
                    json.dumps(filter_outcome.reasons, ensure_ascii=True),
                    json.dumps(filter_outcome.skipped_checks, ensure_ascii=True),
                    json.dumps(risk.risk_flags, ensure_ascii=True),
                    risk.holders,
                    risk.top10_concentration,
                    score.llm_risk_comment,
                    score.llm_action_hint,
                    json.dumps(score.llm_reasons, ensure_ascii=True),
                    int(score.llm_failed),
                ),
            )
            return int(cursor.lastrowid)

    def has_recent_alert(self, token_address: str, pair_address: str, cooldown_minutes: int) -> bool:
        cutoff = _utc_now() - timedelta(minutes=cooldown_minutes)
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT 1
                FROM alerts
                WHERE (token_address = ? OR pair_address = ?)
                  AND created_at >= ?
                LIMIT 1
                """,
                (token_address, pair_address, _to_sqlite_ts(cutoff)),
            ).fetchone()
            return row is not None

    def insert_alert(self, candidate: Candidate, message: str, dry_run: bool, status: str, sent: bool) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO alerts (
                    signal_id, chain_id, pair_address, token_address,
                    final_score, message, dry_run, status, sent_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    candidate.signal_id,
                    candidate.pair.chain_id,
                    candidate.pair.pair_address,
                    candidate.pair.base_token_address,
                    candidate.score.final_score,
                    message,
                    int(dry_run),
                    status,
                    _utc_now().isoformat() if sent else None,
                ),
            )
            return int(cursor.lastrowid)

    def enqueue_recheck_jobs(
        self,
        candidate: Candidate,
        source_alert_id: int,
        scheduled_minutes: Sequence[int] = (5, 15),
    ) -> None:
        now = _utc_now()
        with self.connect() as conn:
            for minute in scheduled_minutes:
                due_at = _to_sqlite_ts(now + timedelta(minutes=int(minute)))
                conn.execute(
                    """
                    INSERT OR IGNORE INTO recheck_jobs (
                        source_alert_id, source_signal_id, chain_id, pair_address, token_address,
                        token_symbol, scheduled_minutes, due_at, status
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'pending')
                    """,
                    (
                        source_alert_id,
                        candidate.signal_id,
                        candidate.pair.chain_id,
                        candidate.pair.pair_address,
                        candidate.pair.base_token_address,
                        candidate.pair.base_token_symbol,
                        int(minute),
                        due_at,
                    ),
                )

    def claim_due_recheck_jobs(self, limit: int) -> list[RecheckJob]:
        now_sql = _to_sqlite_ts(_utc_now())
        jobs: list[RecheckJob] = []
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT
                    id, source_alert_id, source_signal_id, chain_id, pair_address, token_address,
                    token_symbol, scheduled_minutes, due_at, status, attempts
                FROM recheck_jobs
                WHERE status = 'pending' AND due_at <= ?
                ORDER BY due_at ASC
                LIMIT ?
                """,
                (now_sql, max(limit, 1)),
            ).fetchall()

            for row in rows:
                updated = conn.execute(
                    """
                    UPDATE recheck_jobs
                    SET status = 'running', attempts = attempts + 1
                    WHERE id = ? AND status = 'pending'
                    """,
                    (row["id"],),
                )
                if updated.rowcount != 1:
                    continue
                jobs.append(
                    RecheckJob(
                        id=int(row["id"]),
                        source_alert_id=int(row["source_alert_id"]),
                        source_signal_id=(
                            int(row["source_signal_id"]) if row["source_signal_id"] is not None else None
                        ),
                        chain_id=str(row["chain_id"]),
                        pair_address=str(row["pair_address"]),
                        token_address=str(row["token_address"]),
                        token_symbol=str(row["token_symbol"]),
                        scheduled_minutes=int(row["scheduled_minutes"]),
                        due_at=_parse_sqlite_ts(str(row["due_at"])),
                        status="running",
                        attempts=int(row["attempts"]) + 1,
                    )
                )
        return jobs

    def mark_recheck_job_done(self, job_id: int) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE recheck_jobs
                SET status = 'done', processed_at = ?, last_error = NULL
                WHERE id = ?
                """,
                (_to_sqlite_ts(_utc_now()), job_id),
            )

    def mark_recheck_job_failed(self, job_id: int, error_message: str) -> None:
        with self.connect() as conn:
            conn.execute(
                """
                UPDATE recheck_jobs
                SET status = 'failed', processed_at = ?, last_error = ?
                WHERE id = ?
                """,
                (_to_sqlite_ts(_utc_now()), error_message[:500], job_id),
            )

    def insert_recheck_result(
        self,
        job: RecheckJob,
        candidate: Candidate,
        status: str,
        timeline: ScoreTimeline,
        delta_from_initial: float,
        delta_from_previous: float,
        message: str,
    ) -> int:
        with self.connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO recheck_results (
                    job_id, source_alert_id, signal_id, chain_id, pair_address, token_address,
                    token_symbol, scheduled_minutes, status,
                    initial_score, score_5m, score_15m, current_score,
                    delta_from_initial, delta_from_previous,
                    rule_score, llm_score, llm_confidence,
                    summary_line, message
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    job.id,
                    job.source_alert_id,
                    candidate.signal_id,
                    candidate.pair.chain_id,
                    candidate.pair.pair_address,
                    candidate.pair.base_token_address,
                    candidate.pair.base_token_symbol,
                    job.scheduled_minutes,
                    status,
                    timeline.initial_score,
                    timeline.score_5m,
                    timeline.score_15m,
                    candidate.score.final_score,
                    delta_from_initial,
                    delta_from_previous,
                    candidate.score.rule_score,
                    candidate.score.llm_score,
                    candidate.score.llm_confidence,
                    (
                        f"{timeline.initial_score:.2f} -> "
                        f"{'--' if timeline.score_5m is None else f'{timeline.score_5m:.2f}'} -> "
                        f"{'--' if timeline.score_15m is None else f'{timeline.score_15m:.2f}'}"
                    ),
                    message,
                ),
            )
            return int(cursor.lastrowid)

    def get_alert_score(self, alert_id: int) -> float | None:
        with self.connect() as conn:
            row = conn.execute(
                "SELECT final_score FROM alerts WHERE id = ? LIMIT 1",
                (alert_id,),
            ).fetchone()
            if row is None:
                return None
            return float(row["final_score"])

    def get_previous_recheck_score(self, source_alert_id: int, scheduled_minutes: int) -> float | None:
        with self.connect() as conn:
            row = conn.execute(
                """
                SELECT current_score
                FROM recheck_results
                WHERE source_alert_id = ?
                  AND scheduled_minutes < ?
                ORDER BY scheduled_minutes DESC
                LIMIT 1
                """,
                (source_alert_id, scheduled_minutes),
            ).fetchone()
            if row is None:
                return None
            return float(row["current_score"])

    def get_timeline_for_alert(self, alert_id: int) -> ScoreTimeline | None:
        initial = self.get_alert_score(alert_id)
        if initial is None:
            return None

        timeline = ScoreTimeline(initial_score=initial)
        with self.connect() as conn:
            rows = conn.execute(
                """
                SELECT scheduled_minutes, current_score
                FROM recheck_results
                WHERE source_alert_id = ?
                """,
                (alert_id,),
            ).fetchall()
            for row in rows:
                minute = int(row["scheduled_minutes"])
                score = float(row["current_score"])
                if minute == 5:
                    timeline.score_5m = score
                elif minute == 15:
                    timeline.score_15m = score
        return timeline
