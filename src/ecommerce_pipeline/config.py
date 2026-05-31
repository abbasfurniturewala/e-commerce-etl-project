from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")


@dataclass(frozen=True)
class Settings:
    source_dir: Path = Path(os.getenv("SOURCE_DIR", PROJECT_ROOT / "data" / "source"))
    landing_dir: Path = Path(os.getenv("LANDING_DIR", PROJECT_ROOT / "data" / "landing"))
    schema_path: Path = Path(os.getenv("SCHEMA_PATH", PROJECT_ROOT / "sql" / "raw_schema.sql"))
    postgres_db: str = os.getenv("POSTGRES_DB", "ecommerce")
    postgres_user: str = os.getenv("POSTGRES_USER", "ecommerce")
    postgres_password: str = os.getenv("POSTGRES_PASSWORD", "ecommerce")
    postgres_host: str = os.getenv("POSTGRES_HOST", "localhost")
    postgres_port: int = int(os.getenv("POSTGRES_PORT", "5432"))

    @property
    def postgres_dsn(self) -> str:
        return (
            f"dbname={self.postgres_db} "
            f"user={self.postgres_user} "
            f"password={self.postgres_password} "
            f"host={self.postgres_host} "
            f"port={self.postgres_port}"
        )
