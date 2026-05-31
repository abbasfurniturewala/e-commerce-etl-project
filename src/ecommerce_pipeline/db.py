from __future__ import annotations

import csv
import hashlib
import json
from datetime import date
from pathlib import Path
from uuid import uuid4

import psycopg
from psycopg import sql

from ecommerce_pipeline.datasets import DATASETS


def initialize_schema(dsn: str, schema_path: Path) -> None:
    with psycopg.connect(dsn) as connection:
        connection.execute(schema_path.read_text(encoding="utf-8"))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def _row_hash(columns: tuple[str, ...], row: dict[str, str]) -> str:
    payload = json.dumps(
        [row.get(column, "") for column in columns],
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _load_file(
    connection: psycopg.Connection,
    batch_id: str,
    table_name: str,
    columns: tuple[str, ...],
    path: Path,
) -> tuple[int, int]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))

    values = [
        (
            _row_hash(columns, row),
            batch_id,
            path.name,
            *(row.get(column, "") for column in columns),
        )
        for row in rows
    ]
    if not values:
        return 0, 0

    metadata_columns = ("_row_hash", "_batch_id", "_source_file")
    statement = sql.SQL("INSERT INTO raw.{} ({}) VALUES ({}) ON CONFLICT DO NOTHING").format(
        sql.Identifier(table_name),
        sql.SQL(", ").join(map(sql.Identifier, metadata_columns + columns)),
        sql.SQL(", ").join(sql.Placeholder() for _ in metadata_columns + columns),
    )
    with connection.cursor() as cursor:
        cursor.executemany(statement, values)
        inserted_row_count = cursor.rowcount
    return len(rows), inserted_row_count


def load_batch(dsn: str, landing_dir: Path, batch_date: date) -> dict[str, int]:
    batch_path = landing_dir / batch_date.isoformat()
    if not batch_path.exists():
        raise FileNotFoundError(f"Landing batch does not exist: {batch_path}")

    batch_id = str(uuid4())
    row_counts: dict[str, int] = {}
    with psycopg.connect(dsn) as connection:
        connection.execute(
            """
            INSERT INTO raw.ingestion_runs (batch_id, batch_date, status)
            VALUES (%s, %s, 'running')
            """,
            (batch_id, batch_date),
        )
        connection.commit()

        try:
            for dataset in DATASETS:
                path = batch_path / dataset.filename
                if not path.exists():
                    raise FileNotFoundError(f"Landing file does not exist: {path}")

                file_hash = _file_sha256(path)
                already_loaded = connection.execute(
                    "SELECT 1 FROM raw.ingested_files WHERE sha256 = %s",
                    (file_hash,),
                ).fetchone()
                if already_loaded:
                    row_counts[dataset.table_name] = 0
                    continue

                source_row_count, inserted_row_count = _load_file(
                    connection,
                    batch_id,
                    dataset.table_name,
                    dataset.columns,
                    path,
                )
                row_counts[dataset.table_name] = inserted_row_count
                connection.execute(
                    """
                    INSERT INTO raw.ingested_files
                        (batch_id, table_name, source_file, sha256, row_count, inserted_row_count)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        batch_id,
                        dataset.table_name,
                        path.name,
                        file_hash,
                        source_row_count,
                        inserted_row_count,
                    ),
                )

            connection.execute(
                """
                UPDATE raw.ingestion_runs
                SET status = 'succeeded', finished_at = now(), row_counts = %s
                WHERE batch_id = %s
                """,
                (json.dumps(row_counts), batch_id),
            )
        except Exception as error:
            connection.rollback()
            connection.execute(
                """
                UPDATE raw.ingestion_runs
                SET status = 'failed', finished_at = now(), error_message = %s
                WHERE batch_id = %s
                """,
                (str(error), batch_id),
            )
            connection.commit()
            raise

    return row_counts
