"""Generate accurate calendar_ganzhi.csv for 2020-01-01 to 2035-12-31.

Data priority:
1. HKO / DATA.GOV.HK Gregorian-Lunar Calendar Conversion Table for verification.
2. lunar_python for Gan-Zhi, solar terms, Jie-Qi month, and daily Gan-Zhi generation.
"""

from __future__ import annotations

import csv
import logging
import random
import sys
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

import requests
from lunar_python import Solar

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wuxing_stock_app import database

APP_DATA_DIR = PROJECT_ROOT / "wuxing_stock_app" / "data"
OUTPUT_CSV = APP_DATA_DIR / "calendar_ganzhi.csv"
ROOT_DATA_CSV = PROJECT_ROOT / "data" / "calendar_ganzhi.csv"
VALIDATION_REPORT = PROJECT_ROOT / "validation_report.md"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "generate_calendar_data.log"

START_DATE = date(2020, 1, 1)
END_DATE = date(2035, 12, 31)
HKO_URL_TEMPLATE = "https://data.weather.gov.hk/weatherAPI/hko_data/calendar/nongli_calendar_{year}.csv"

FIELDNAMES = [
    "date",
    "weekday",
    "solar_term",
    "lunar_year",
    "lunar_month",
    "lunar_day",
    "lunar_year_ganzhi",
    "lichun_year_ganzhi",
    "month_ganzhi",
    "day_ganzhi",
    "year_gan",
    "year_zhi",
    "month_gan",
    "month_zhi",
    "day_gan",
    "day_zhi",
    "year_element",
    "month_element",
    "day_element",
    "main_element",
    "secondary_element",
    "source",
    "verified",
    "updated_at",
    "confidence",
]

GAN_ELEMENTS = {
    "甲": "wood",
    "乙": "wood",
    "丙": "fire",
    "丁": "fire",
    "戊": "earth",
    "己": "earth",
    "庚": "metal",
    "辛": "metal",
    "壬": "water",
    "癸": "water",
}

ZHI_ELEMENTS = {
    "寅": "wood",
    "卯": "wood",
    "巳": "fire",
    "午": "fire",
    "辰": "earth",
    "戌": "earth",
    "丑": "earth",
    "未": "earth",
    "申": "metal",
    "酉": "metal",
    "亥": "water",
    "子": "water",
}

WEEKDAY_LABELS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
SOURCE_VERIFIED = "HKO_DATA_GOV_HK_GREGORIAN_LUNAR_TABLE;lunar_python_1.4.8"
SOURCE_GENERATED = "lunar_python_1.4.8;HKO_DATA_GOV_HK_UNAVAILABLE_FOR_YEAR"


@dataclass(frozen=True)
class HkoLunarRow:
    lunar_year_ganzhi: str
    lunar_month_label: str
    lunar_day_label: str


def main() -> None:
    setup_logging()
    logging.info("step=calendar_generate_start range=%s:%s", START_DATE.isoformat(), END_DATE.isoformat())
    APP_DATA_DIR.mkdir(parents=True, exist_ok=True)
    hko_rows = load_hko_rows(START_DATE.year, END_DATE.year)
    logging.info("step=hko_rows_loaded count=%s", len(hko_rows))
    generated_rows = generate_rows(START_DATE, END_DATE, hko_rows)
    logging.info("step=calendar_rows_generated count=%s", len(generated_rows))
    database.initialize_database()
    ensure_calendar_schema()
    save_calendar_to_sqlite(generated_rows)
    logging.info("step=calendar_sqlite_written count=%s", len(generated_rows))
    write_csv(generated_rows, OUTPUT_CSV)
    logging.info("step=calendar_csv_written path=%s", OUTPUT_CSV)
    ROOT_DATA_CSV.parent.mkdir(parents=True, exist_ok=True)
    write_csv(generated_rows, ROOT_DATA_CSV)
    logging.info("step=calendar_csv_written path=%s", ROOT_DATA_CSV)
    report = build_validation_report(generated_rows, hko_rows, sample_size=30)
    VALIDATION_REPORT.write_text(report, encoding="utf-8")
    logging.info("step=validation_report_written path=%s", VALIDATION_REPORT)
    print(f"Generated {len(generated_rows)} rows: {OUTPUT_CSV}")
    print(f"Generated mirror CSV: {ROOT_DATA_CSV}")
    print(f"Validation report: {VALIDATION_REPORT}")


def load_hko_rows(start_year: int, end_year: int) -> dict[str, HkoLunarRow]:
    """Download HKO Gregorian-Lunar conversion tables by Gregorian year."""
    rows: dict[str, HkoLunarRow] = {}
    for year in range(start_year, end_year + 1):
        url = HKO_URL_TEMPLATE.format(year=year)
        response = requests.get(url, timeout=30, allow_redirects=False)
        if response.status_code != 200:
            logging.info("step=hko_year_unavailable year=%s status=%s", year, response.status_code)
            continue
        logging.info("step=hko_year_loaded year=%s", year)
        text = response.content.decode("utf-8-sig")
        reader = csv.DictReader(text.splitlines())
        for item in reader:
            parsed_date = parse_hko_date(item["Gregorian Date"], year)
            rows[parsed_date.isoformat()] = HkoLunarRow(
                lunar_year_ganzhi=item["Chinese year (Gan-Zhi)"].removesuffix("年"),
                lunar_month_label=item["Lunar month"],
                lunar_day_label=item["Lunar Date"],
            )
    return rows


def generate_rows(
    start_date: date,
    end_date: date,
    hko_rows: dict[str, HkoLunarRow],
) -> list[dict[str, Any]]:
    rows = []
    current = start_date
    while current <= end_date:
        rows.append(generate_row(current, hko_rows.get(current.isoformat())))
        current += timedelta(days=1)
    return rows


def generate_row(current: date, hko_row: HkoLunarRow | None) -> dict[str, Any]:
    lunar = Solar.fromYmd(current.year, current.month, current.day).getLunar()
    lunar_year_ganzhi = lunar.getYearInGanZhi()
    lichun_year_ganzhi = lunar.getYearInGanZhiByLiChun()
    month_ganzhi = lunar.getMonthInGanZhi()
    day_ganzhi = lunar.getDayInGanZhi()

    year_gan, year_zhi = split_ganzhi(lichun_year_ganzhi)
    month_gan, month_zhi = split_ganzhi(month_ganzhi)
    day_gan, day_zhi = split_ganzhi(day_ganzhi)

    updated_at = datetime.now().replace(microsecond=0).isoformat()
    row = {
        "date": current.isoformat(),
        "weekday": WEEKDAY_LABELS[current.weekday()],
        "solar_term": lunar.getJieQi(),
        "lunar_year": lunar.getYear(),
        "lunar_month": lunar.getMonth(),
        "lunar_day": lunar.getDay(),
        "lunar_year_ganzhi": lunar_year_ganzhi,
        "lichun_year_ganzhi": lichun_year_ganzhi,
        "month_ganzhi": month_ganzhi,
        "day_ganzhi": day_ganzhi,
        "year_gan": year_gan,
        "year_zhi": year_zhi,
        "month_gan": month_gan,
        "month_zhi": month_zhi,
        "day_gan": day_gan,
        "day_zhi": day_zhi,
        "year_element": gan_to_element(year_gan),
        "month_element": gan_to_element(month_gan),
        "day_element": gan_to_element(day_gan),
        "main_element": gan_to_element(day_gan),
        "secondary_element": gan_to_element(month_gan),
        "source": SOURCE_GENERATED,
        "verified": "false",
        "updated_at": updated_at,
        "confidence": 70,
    }

    if hko_row and matches_hko(lunar, lunar_year_ganzhi, hko_row):
        row["source"] = SOURCE_VERIFIED
        row["verified"] = "true"
        row["confidence"] = 100
    return row


def matches_hko(lunar: Any, lunar_year_ganzhi: str, hko_row: HkoLunarRow) -> bool:
    return (
        lunar_year_ganzhi == hko_row.lunar_year_ganzhi
        and lunar_month_to_hko_label(lunar.getMonth()) == hko_row.lunar_month_label
        and lunar_day_to_hko_label(lunar.getDay()) == hko_row.lunar_day_label
    )


def build_validation_report(
    generated_rows: list[dict[str, Any]],
    hko_rows: dict[str, HkoLunarRow],
    *,
    sample_size: int,
) -> str:
    random.seed(20260629)
    hko_sample_pool = [row for row in generated_rows if row["source"] == SOURCE_VERIFIED]
    sample = random.sample(hko_sample_pool, min(sample_size, len(hko_sample_pool)))
    verified_count = sum(1 for row in generated_rows if row["verified"] == "true")
    lines = [
        "# calendar_ganzhi.csv Validation Report",
        "",
        f"- Date range: {START_DATE.isoformat()} to {END_DATE.isoformat()}",
        f"- Generated rows: {len(generated_rows)}",
        f"- HKO rows loaded: {len(hko_rows)}",
        f"- Verified rows: {verified_count}",
        f"- Verification rate: {verified_count / len(generated_rows):.2%}",
        f"- HKO-verified random sample size: {len(sample)}",
        f"- Output source field: HKO verified rows use `{SOURCE_VERIFIED}`; generated-only rows use `{SOURCE_GENERATED}`",
        "- Output confidence field: 100 for HKO-verified rows, 70 for generated-only rows.",
        "",
        "| Date | Lunar Year GZ | LiChun Year GZ | Month GZ | Day GZ | HKO Verified |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for row in sample:
        lines.append(
            "| {date} | {lunar_year_ganzhi} | {lichun_year_ganzhi} | {month_ganzhi} | "
            "{day_ganzhi} | {verified} |".format(**row)
        )
    lines.extend(
        [
            "",
            "Notes:",
            "- HKO / DATA.GOV.HK is used to verify Gregorian date, lunar year Gan-Zhi, lunar month and lunar day.",
            "- lunar_python generates solar terms, LiChun year Gan-Zhi, Jie-Qi month Gan-Zhi and daily Gan-Zhi.",
            "- The analysis engine should use `lichun_year_ganzhi` as the default year Gan-Zhi.",
            "- `month_ganzhi` uses Jie-Qi month, not Gregorian month.",
        ]
    )
    return "\n".join(lines) + "\n"


def write_csv(rows: list[dict[str, Any]], path: Path) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def save_calendar_to_sqlite(rows: list[dict[str, Any]]) -> None:
    database.execute_many(
        """
        INSERT OR REPLACE INTO calendar_ganzhi (
          date, weekday, solar_term, lunar_year, lunar_month, lunar_day,
          lunar_year_ganzhi, lichun_year_ganzhi, month_ganzhi, day_ganzhi,
          year_gan, year_zhi, month_gan, month_zhi, day_gan, day_zhi,
          year_element, month_element, day_element, main_element, secondary_element,
          source, verified, updated_at, confidence
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            tuple(row[field] for field in FIELDNAMES)
            for row in rows
        ],
    )


def ensure_calendar_schema() -> None:
    existing = {
        row["name"]
        for row in database.fetch_all("PRAGMA table_info(calendar_ganzhi)")
    }
    for column, ddl in {
        "updated_at": "TEXT NOT NULL DEFAULT ''",
        "confidence": "INTEGER NOT NULL DEFAULT 70",
    }.items():
        if column not in existing:
            database.execute(f"ALTER TABLE calendar_ganzhi ADD COLUMN {column} {ddl}")


def setup_logging() -> None:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
            logging.StreamHandler(),
        ],
        force=True,
    )


def parse_hko_date(value: str, year: int) -> date:
    day_text, month_text, year_text = value.split("-")
    month = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }[month_text]
    parsed_year = 2000 + int(year_text)
    if parsed_year != year:
        raise ValueError(f"HKO year mismatch: {value}")
    return date(parsed_year, month, int(day_text))


def split_ganzhi(value: str) -> tuple[str, str]:
    if len(value) != 2:
        raise ValueError(f"invalid Gan-Zhi value: {value}")
    return value[0], value[1]


def gan_to_element(gan: str) -> str:
    try:
        return GAN_ELEMENTS[gan]
    except KeyError as exc:
        raise ValueError(f"unsupported heavenly stem: {gan}") from exc


def zhi_to_element(zhi: str) -> str:
    try:
        return ZHI_ELEMENTS[zhi]
    except KeyError as exc:
        raise ValueError(f"unsupported earthly branch: {zhi}") from exc


def lunar_month_to_hko_label(month: int) -> str:
    leap_prefix = "閏" if month < 0 else ""
    month_abs = abs(month)
    labels = {
        1: "正月",
        2: "二月",
        3: "三月",
        4: "四月",
        5: "五月",
        6: "六月",
        7: "七月",
        8: "八月",
        9: "九月",
        10: "十月",
        11: "十一月",
        12: "十二月",
    }
    return leap_prefix + labels[month_abs]


def lunar_day_to_hko_label(day: int) -> str:
    labels = {
        1: "初一",
        2: "初二",
        3: "初三",
        4: "初四",
        5: "初五",
        6: "初六",
        7: "初七",
        8: "初八",
        9: "初九",
        10: "初十",
        11: "十一",
        12: "十二",
        13: "十三",
        14: "十四",
        15: "十五",
        16: "十六",
        17: "十七",
        18: "十八",
        19: "十九",
        20: "二十",
        21: "廿一",
        22: "廿二",
        23: "廿三",
        24: "廿四",
        25: "廿五",
        26: "廿六",
        27: "廿七",
        28: "廿八",
        29: "廿九",
        30: "三十",
    }
    return labels[day]


if __name__ == "__main__":
    main()
