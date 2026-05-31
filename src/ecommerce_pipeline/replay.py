from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import date, datetime
from pathlib import Path

from ecommerce_pipeline.datasets import DATASETS


class SourceDataError(ValueError):
    """Raised when source data is missing or malformed."""


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise SourceDataError(f"Missing source file: {path}")

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_csv(
    path: Path, fieldnames: tuple[str, ...], rows: Iterable[dict[str, str]]
) -> int:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return len(rows)


def _purchase_date(order: dict[str, str]) -> date:
    try:
        return datetime.fromisoformat(order["order_purchase_timestamp"]).date()
    except (KeyError, ValueError) as error:
        raise SourceDataError("Orders contain an invalid purchase timestamp.") from error


def source_summary(source_dir: Path) -> dict[str, object]:
    orders = _read_csv(source_dir / "olist_orders_dataset.csv")
    if not orders:
        raise SourceDataError("The orders source file is empty.")

    dates = [_purchase_date(order) for order in orders]
    missing = [
        dataset.filename
        for dataset in DATASETS
        if not (source_dir / dataset.filename).exists()
    ]
    return {
        "orders": len(orders),
        "first_order_date": min(dates),
        "last_order_date": max(dates),
        "missing_files": missing,
    }


def generate_daily_batch(source_dir: Path, landing_dir: Path, batch_date: date) -> dict[str, int]:
    orders = [
        row
        for row in _read_csv(source_dir / "olist_orders_dataset.csv")
        if _purchase_date(row) == batch_date
    ]
    if not orders:
        raise SourceDataError(f"No orders found for {batch_date.isoformat()}.")

    order_ids = {row["order_id"] for row in orders}
    order_items = [
        row
        for row in _read_csv(source_dir / "olist_order_items_dataset.csv")
        if row["order_id"] in order_ids
    ]
    payments = [
        row
        for row in _read_csv(source_dir / "olist_order_payments_dataset.csv")
        if row["order_id"] in order_ids
    ]
    reviews = [
        row
        for row in _read_csv(source_dir / "olist_order_reviews_dataset.csv")
        if row["order_id"] in order_ids
    ]

    customer_ids = {row["customer_id"] for row in orders}
    customers = [
        row
        for row in _read_csv(source_dir / "olist_customers_dataset.csv")
        if row["customer_id"] in customer_ids
    ]

    product_ids = {row["product_id"] for row in order_items}
    products = [
        row
        for row in _read_csv(source_dir / "olist_products_dataset.csv")
        if row["product_id"] in product_ids
    ]

    seller_ids = {row["seller_id"] for row in order_items}
    sellers = [
        row
        for row in _read_csv(source_dir / "olist_sellers_dataset.csv")
        if row["seller_id"] in seller_ids
    ]

    category_names = {row["product_category_name"] for row in products}
    categories = [
        row
        for row in _read_csv(source_dir / "product_category_name_translation.csv")
        if row["product_category_name"] in category_names
    ]

    zip_codes = {
        row["customer_zip_code_prefix"] for row in customers
    } | {
        row["seller_zip_code_prefix"] for row in sellers
    }
    geolocation = [
        row
        for row in _read_csv(source_dir / "olist_geolocation_dataset.csv")
        if row["geolocation_zip_code_prefix"] in zip_codes
    ]

    rows_by_filename = {
        "olist_orders_dataset.csv": orders,
        "olist_order_items_dataset.csv": order_items,
        "olist_order_payments_dataset.csv": payments,
        "olist_order_reviews_dataset.csv": reviews,
        "olist_customers_dataset.csv": customers,
        "olist_products_dataset.csv": products,
        "olist_sellers_dataset.csv": sellers,
        "olist_geolocation_dataset.csv": geolocation,
        "product_category_name_translation.csv": categories,
    }

    batch_dir = landing_dir / batch_date.isoformat()
    return {
        dataset.filename: _write_csv(
            batch_dir / dataset.filename,
            dataset.columns,
            rows_by_filename[dataset.filename],
        )
        for dataset in DATASETS
    }
