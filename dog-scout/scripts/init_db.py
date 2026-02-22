#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from dog_scout.config import Settings
from dog_scout.storage import Database


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize dog-scout sqlite database")
    parser.add_argument("--db-path", default=None, help="Override sqlite db path")
    return parser.parse_args()


def main() -> None:
    load_dotenv()
    args = parse_args()
    settings = Settings.from_env()
    db_path = Path(args.db_path).expanduser() if args.db_path else settings.db_path

    db = Database(db_path)
    db.ensure_initialized()
    print(f"Initialized database at: {db_path}")


if __name__ == "__main__":
    main()
