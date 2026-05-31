from __future__ import annotations

import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from ecommerce_pipeline.replay import generate_daily_batch, source_summary


def _write_csv(path: Path, fieldnames: tuple[str, ...], rows: list[dict[str, str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _build_source(source_dir: Path) -> None:
    _write_csv(
        source_dir / "olist_orders_dataset.csv",
        (
            "order_id",
            "customer_id",
            "order_status",
            "order_purchase_timestamp",
            "order_approved_at",
            "order_delivered_carrier_date",
            "order_delivered_customer_date",
            "order_estimated_delivery_date",
        ),
        [
            {
                "order_id": "order-1",
                "customer_id": "customer-1",
                "order_status": "delivered",
                "order_purchase_timestamp": "2017-01-05 10:00:00",
            },
            {
                "order_id": "order-2",
                "customer_id": "customer-2",
                "order_status": "delivered",
                "order_purchase_timestamp": "2017-01-06 11:00:00",
            },
        ],
    )
    _write_csv(
        source_dir / "olist_order_items_dataset.csv",
        ("order_id", "order_item_id", "product_id", "seller_id", "shipping_limit_date", "price", "freight_value"),
        [
            {"order_id": "order-1", "order_item_id": "1", "product_id": "product-1", "seller_id": "seller-1"},
            {"order_id": "order-2", "order_item_id": "1", "product_id": "product-2", "seller_id": "seller-2"},
        ],
    )
    _write_csv(
        source_dir / "olist_order_payments_dataset.csv",
        ("order_id", "payment_sequential", "payment_type", "payment_installments", "payment_value"),
        [{"order_id": "order-1", "payment_sequential": "1", "payment_type": "credit_card"}],
    )
    _write_csv(
        source_dir / "olist_order_reviews_dataset.csv",
        ("review_id", "order_id", "review_score", "review_comment_title", "review_comment_message", "review_creation_date", "review_answer_timestamp"),
        [{"review_id": "review-1", "order_id": "order-1", "review_score": "5"}],
    )
    _write_csv(
        source_dir / "olist_customers_dataset.csv",
        ("customer_id", "customer_unique_id", "customer_zip_code_prefix", "customer_city", "customer_state"),
        [{"customer_id": "customer-1", "customer_unique_id": "unique-1", "customer_zip_code_prefix": "1000"}],
    )
    _write_csv(
        source_dir / "olist_products_dataset.csv",
        ("product_id", "product_category_name", "product_name_lenght", "product_description_lenght", "product_photos_qty", "product_weight_g", "product_length_cm", "product_height_cm", "product_width_cm"),
        [{"product_id": "product-1", "product_category_name": "books"}],
    )
    _write_csv(
        source_dir / "olist_sellers_dataset.csv",
        ("seller_id", "seller_zip_code_prefix", "seller_city", "seller_state"),
        [{"seller_id": "seller-1", "seller_zip_code_prefix": "2000"}],
    )
    _write_csv(
        source_dir / "olist_geolocation_dataset.csv",
        ("geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng", "geolocation_city", "geolocation_state"),
        [
            {"geolocation_zip_code_prefix": "1000", "geolocation_city": "city-a"},
            {"geolocation_zip_code_prefix": "2000", "geolocation_city": "city-b"},
            {"geolocation_zip_code_prefix": "3000", "geolocation_city": "city-c"},
        ],
    )
    _write_csv(
        source_dir / "product_category_name_translation.csv",
        ("product_category_name", "product_category_name_english"),
        [{"product_category_name": "books", "product_category_name_english": "books"}],
    )


class ReplayTestCase(unittest.TestCase):
    def test_source_summary_reports_date_range(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir)
            _build_source(source_dir)

            summary = source_summary(source_dir)

            self.assertEqual(summary["orders"], 2)
            self.assertEqual(summary["first_order_date"], date(2017, 1, 5))
            self.assertEqual(summary["last_order_date"], date(2017, 1, 6))
            self.assertEqual(summary["missing_files"], [])

    def test_generate_daily_batch_keeps_only_related_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            source_dir = Path(temp_dir) / "source"
            landing_dir = Path(temp_dir) / "landing"
            source_dir.mkdir()
            _build_source(source_dir)

            counts = generate_daily_batch(source_dir, landing_dir, date(2017, 1, 5))

            batch_dir = landing_dir / "2017-01-05"
            self.assertEqual(counts["olist_orders_dataset.csv"], 1)
            self.assertEqual(
                [row["order_id"] for row in _read_csv(batch_dir / "olist_orders_dataset.csv")],
                ["order-1"],
            )
            self.assertEqual(
                [row["product_id"] for row in _read_csv(batch_dir / "olist_products_dataset.csv")],
                ["product-1"],
            )
            self.assertEqual(
                {
                    row["geolocation_zip_code_prefix"]
                    for row in _read_csv(batch_dir / "olist_geolocation_dataset.csv")
                },
                {"1000", "2000"},
            )


if __name__ == "__main__":
    unittest.main()
