from __future__ import annotations

import argparse
import logging
import time
from dataclasses import replace

from dotenv import load_dotenv

from dog_scout.config import Settings
from dog_scout.logging_config import setup_logging
from dog_scout.pipeline import ScoutPipeline
from dog_scout.storage import Database

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Dog Scout scanner")
    parser.add_argument("--mode", choices=["once", "loop"], default="once")
    parser.add_argument("--interval", type=int, default=None, help="loop interval seconds")
    parser.add_argument("--dry-run", action="store_true", help="force dry-run output mode")
    parser.add_argument(
        "--use-mock-data",
        action="store_true",
        help="scan built-in mock dataset instead of Dexscreener API",
    )
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    setup_logging()

    args = parse_args()
    settings = Settings.from_env()

    if args.interval is not None:
        settings = replace(settings, loop_interval_seconds=max(args.interval, 5))
    if args.dry_run:
        settings = replace(settings, dry_run=True)
    if args.use_mock_data:
        settings = replace(settings, use_mock_data=True)

    db = Database(settings.db_path)
    db.ensure_initialized()

    pipeline = ScoutPipeline(settings=settings, db=db)

    if args.mode == "once":
        result = pipeline.run_once()
        logger.info(
            "single run done | fetched=%s passed=%s selected=%s rechecked=%s",
            result.fetched_pairs,
            result.passed_filters,
            result.selected,
            result.rechecked,
        )
        return

    logger.info("loop mode started | interval=%s sec", settings.loop_interval_seconds)
    try:
        while True:
            pipeline.run_once()
            time.sleep(settings.loop_interval_seconds)
    except KeyboardInterrupt:
        logger.info("loop mode stopped")


if __name__ == "__main__":
    main()
