from __future__ import annotations

import argparse
import json
from datetime import date

import psycopg

from ecommerce_pipeline.config import Settings
from ecommerce_pipeline.db import initialize_schema, load_batch
from ecommerce_pipeline.replay import SourceDataError, generate_daily_batch, source_summary


def _iso_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Use an ISO date such as 2017-01-05.") from error


def _print_json(payload: object) -> None:
    print(json.dumps(payload, indent=2, default=str))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the local e-commerce pipeline.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("inspect-source", help="Validate source files and show the order date range.")
    subparsers.add_parser("init-db", help="Create the PostgreSQL raw schema.")

    replay_parser = subparsers.add_parser("replay", help="Generate one daily landing batch.")
    replay_parser.add_argument("--date", required=True, type=_iso_date, dest="batch_date")

    ingest_parser = subparsers.add_parser("ingest", help="Load one daily landing batch into PostgreSQL.")
    ingest_parser.add_argument("--date", required=True, type=_iso_date, dest="batch_date")

    run_parser = subparsers.add_parser("run-batch", help="Generate and ingest one daily batch.")
    run_parser.add_argument("--date", required=True, type=_iso_date, dest="batch_date")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    settings = Settings()

    try:
        if args.command == "inspect-source":
            _print_json(source_summary(settings.source_dir))
        elif args.command == "init-db":
            initialize_schema(settings.postgres_dsn, settings.schema_path)
            print("Raw schema initialized.")
        elif args.command == "replay":
            _print_json(generate_daily_batch(settings.source_dir, settings.landing_dir, args.batch_date))
        elif args.command == "ingest":
            _print_json(load_batch(settings.postgres_dsn, settings.landing_dir, args.batch_date))
        elif args.command == "run-batch":
            initialize_schema(settings.postgres_dsn, settings.schema_path)
            _print_json(generate_daily_batch(settings.source_dir, settings.landing_dir, args.batch_date))
            _print_json(load_batch(settings.postgres_dsn, settings.landing_dir, args.batch_date))
    except (FileNotFoundError, SourceDataError, psycopg.Error) as error:
        raise SystemExit(f"Error: {error}") from None


if __name__ == "__main__":
    main()
