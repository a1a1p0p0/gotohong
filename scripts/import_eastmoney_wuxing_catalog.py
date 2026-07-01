"""Import annotated Eastmoney board wuxing catalog as the ranking standard."""

from __future__ import annotations

import csv
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wuxing_stock_app import database


SOURCE_XLSX = Path(r"C:\Users\Administrator\Downloads\eastmoney_board_catalog_wuxing_annotated_20260701.xlsx")
OUTPUT_CSV = PROJECT_ROOT / "data" / "astock_board_wuxing_profiles.csv"
LOG_FILE = PROJECT_ROOT / "logs" / "import_eastmoney_wuxing_catalog.log"
SOURCE_NAME = "eastmoney_board_catalog_wuxing_annotated_20260701.xlsx"

ELEMENT_MAP = {"木": "wood", "火": "fire", "土": "earth", "金": "metal", "水": "water"}
SHEETS = (
    ("行业板块名称", "industry", "行业板块名称"),
    ("概念板块名称", "concept", "概念板块名称"),
)
OUTPUT_FIELDS = [
    "board_code",
    "board_name",
    "board_type",
    "category",
    "subcategory",
    "main_element",
    "secondary_element",
    "wood_score",
    "fire_score",
    "earth_score",
    "metal_score",
    "water_score",
    "confidence",
    "reason",
    "paid_required",
    "source",
    "updated_at",
    "need_review",
]


def main() -> None:
    rows = import_catalog()
    print(f"Imported {len(rows)} boards: {OUTPUT_CSV}")


def import_catalog(
    source_xlsx: Path = SOURCE_XLSX,
    output_csv: Path = OUTPUT_CSV,
    db_path: Path | str = database.DB_PATH,
) -> list[dict[str, Any]]:
    if not source_xlsx.exists():
        raise FileNotFoundError(source_xlsx)

    updated_at = datetime.now().replace(microsecond=0).isoformat()
    rows: list[dict[str, Any]] = []
    for sheet_name, board_type, name_column in SHEETS:
        frame = pd.read_excel(source_xlsx, sheet_name=sheet_name)
        for _, row in frame.iterrows():
            rows.append(normalize_row(row, board_type=board_type, name_column=name_column, updated_at=updated_at))

    database.initialize_database(db_path)
    save_to_sqlite(rows, db_path=db_path)
    write_csv(output_csv, rows)
    write_log(source_xlsx, rows, updated_at)
    return rows


def normalize_row(row: Any, *, board_type: str, name_column: str, updated_at: str) -> dict[str, Any]:
    main_element_cn = clean_text(row.get("主五行"))
    secondary_element_cn = clean_text(row.get("副五行"))
    main_element = ELEMENT_MAP[main_element_cn]
    secondary_element = ELEMENT_MAP[secondary_element_cn]
    main_weight = int(row.get("主权重") or 0)
    secondary_weight = int(row.get("副权重") or 0)
    scores = {element: 0 for element in ELEMENT_MAP.values()}
    scores[main_element] = main_weight
    scores[secondary_element] = secondary_weight
    board_name = clean_text(row.get(name_column))
    level = clean_text(row.get("行业层级"))

    return {
        "board_code": clean_text(row.get("板块代码")),
        "board_name": board_name,
        "board_type": board_type,
        "category": level if board_type == "industry" else "概念板块",
        "subcategory": board_name,
        "main_element": main_element,
        "secondary_element": secondary_element,
        "wood_score": scores["wood"],
        "fire_score": scores["fire"],
        "earth_score": scores["earth"],
        "metal_score": scores["metal"],
        "water_score": scores["water"],
        "confidence": 100,
        "reason": clean_text(row.get("判断理由")),
        "paid_required": "true",
        "source": SOURCE_NAME,
        "updated_at": updated_at,
        "need_review": "false",
    }


def clean_text(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def save_to_sqlite(rows: list[dict[str, Any]], *, db_path: Path | str) -> None:
    database.execute("DELETE FROM astock_boards", db_path=db_path)
    database.execute("DELETE FROM astock_board_wuxing_profiles", db_path=db_path)
    database.execute_many(
        """
        INSERT OR REPLACE INTO astock_boards (
          board_type, board_code, board_name, source, member_count, updated_at, confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                row["board_type"],
                row["board_code"],
                row["board_name"],
                row["source"],
                0,
                row["updated_at"],
                row["confidence"],
            )
            for row in rows
        ],
        db_path,
    )
    database.execute_many(
        """
        INSERT OR REPLACE INTO astock_board_wuxing_profiles (
          board_code, board_name, board_type, category, subcategory,
          main_element, secondary_element, wood_score, fire_score, earth_score,
          metal_score, water_score, confidence, reason, paid_required,
          source, updated_at, need_review
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [tuple(row[field] for field in OUTPUT_FIELDS) for row in rows],
        db_path,
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(rows)


def write_log(source_xlsx: Path, rows: list[dict[str, Any]], updated_at: str) -> None:
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    industry_count = sum(1 for row in rows if row["board_type"] == "industry")
    concept_count = sum(1 for row in rows if row["board_type"] == "concept")
    LOG_FILE.write_text(
        "\n".join(
            [
                f"updated_at={updated_at}",
                f"source={source_xlsx}",
                f"total={len(rows)}",
                f"industry={industry_count}",
                f"concept={concept_count}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
