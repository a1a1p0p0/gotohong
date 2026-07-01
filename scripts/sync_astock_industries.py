"""Sync A-share industry and concept board raw data.

This script only synchronizes and cleans raw board data. It does not produce
any wuxing conclusion.
"""

from __future__ import annotations

import csv
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Callable

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from wuxing_stock_app import database

DATA_DIR = PROJECT_ROOT / "data"
INDUSTRY_CSV = DATA_DIR / "astock_industry_raw.csv"
CONCEPT_CSV = DATA_DIR / "astock_concept_raw.csv"
MEMBERS_CSV = DATA_DIR / "astock_board_members.csv"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_FILE = LOG_DIR / "sync_astock_industries.log"

PUSH2_CLIST_URL = "https://push2.eastmoney.com/api/qt/clist/get"
SOURCE = "eastmoney_push2_clist"
BOARD_FIELDS = ["board_type", "board_code", "board_name", "source", "member_count", "updated_at", "confidence"]
MEMBER_FIELDS = ["board_code", "board_name", "stock_code", "stock_name", "source", "updated_at", "confidence"]

BOARD_FS = {
    "industry": "m:90+t:2",
    "concept": "m:90+t:3",
}


def main() -> None:
    setup_logging()
    result = sync_astock_industries()
    print(
        "Synced {industry_count} industry boards, {concept_count} concept boards, "
        "{member_count} board members.".format(**result)
    )


def sync_astock_industries(
    *,
    db_path: Path | str = database.DB_PATH,
    board_fetcher: Callable[[str], list[dict[str, object]]] | None = None,
    member_fetcher: Callable[[dict[str, object]], list[dict[str, object]]] | None = None,
    updated_at: str | None = None,
) -> dict[str, int]:
    """Sync industry boards, concept boards, and board members."""
    setup_logging()
    logging.info("step=sync_start")
    database.initialize_database(db_path)
    ensure_astock_schema(db_path)
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    updated_at = updated_at or datetime.now().replace(microsecond=0).isoformat()
    board_fetcher = board_fetcher or fetch_boards
    member_fetcher = member_fetcher or fetch_board_members

    industry_boards = _sync_board_type("industry", board_fetcher, member_fetcher, updated_at)
    logging.info("step=industry_boards_synced count=%s", len(industry_boards))
    concept_boards = _sync_board_type("concept", board_fetcher, member_fetcher, updated_at)
    logging.info("step=concept_boards_synced count=%s", len(concept_boards))
    all_boards = industry_boards + concept_boards
    all_members = [member for board in all_boards for member in board.pop("_members")]
    logging.info("step=board_members_synced count=%s", len(all_members))

    save_to_sqlite(all_boards, all_members, db_path=db_path)
    logging.info("step=sqlite_written boards=%s members=%s", len(all_boards), len(all_members))
    write_csv(INDUSTRY_CSV, [b for b in all_boards if b["board_type"] == "industry"], BOARD_FIELDS)
    logging.info("step=csv_written path=%s", INDUSTRY_CSV)
    write_csv(CONCEPT_CSV, [b for b in all_boards if b["board_type"] == "concept"], BOARD_FIELDS)
    logging.info("step=csv_written path=%s", CONCEPT_CSV)
    write_csv(MEMBERS_CSV, all_members, MEMBER_FIELDS)
    logging.info("step=csv_written path=%s", MEMBERS_CSV)

    return {
        "industry_count": len([b for b in all_boards if b["board_type"] == "industry"]),
        "concept_count": len([b for b in all_boards if b["board_type"] == "concept"]),
        "member_count": len(all_members),
    }


def fetch_boards(board_type: str) -> list[dict[str, object]]:
    """Fetch all industry or concept boards from Eastmoney clist."""
    if board_type not in BOARD_FS:
        raise ValueError("board_type only supports industry, concept")

    boards: list[dict[str, object]] = []
    page = 1
    page_size = 100
    while True:
        params = {
            "pn": str(page),
            "pz": str(page_size),
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": BOARD_FS[board_type],
            "fields": "f12,f14,f104,f105",
        }
        data = em_get_json(PUSH2_CLIST_URL, params=params)
        payload = data.get("data") or {}
        items = payload.get("diff") or []
        if not items:
            break
        for item in items:
            if item.get("f12") and item.get("f14"):
                boards.append(
                    clean_board(
                        board_type=board_type,
                        board_code=str(item.get("f12", "")).strip(),
                        board_name=str(item.get("f14", "")).strip(),
                        member_count=0,
                        updated_at="",
                    )
                )
        total = int(payload.get("total") or len(boards))
        logging.info("step=board_page_loaded board_type=%s page=%s rows=%s total=%s", board_type, page, len(items), total)
        if len(boards) >= total or len(items) < page_size:
            break
        page += 1
    return boards


def fetch_board_members(board: dict[str, object]) -> list[dict[str, object]]:
    """Fetch component stocks for one Eastmoney board."""
    board_code = str(board["board_code"])
    board_name = str(board["board_name"])
    members: list[dict[str, object]] = []
    page = 1
    while True:
        params = {
            "pn": str(page),
            "pz": "500",
            "po": "1",
            "np": "1",
            "fltt": "2",
            "invt": "2",
            "fid": "f3",
            "fs": f"b:{board_code}",
            "fields": "f12,f14",
        }
        data = em_get_json(PUSH2_CLIST_URL, params=params)
        payload = data.get("data") or {}
        items = payload.get("diff") or []
        if not items:
            break
        for item in items:
            stock_code = str(item.get("f12", "")).strip()
            stock_name = str(item.get("f14", "")).strip()
            if stock_code and stock_name:
                members.append(
                    {
                        "board_code": board_code,
                        "board_name": board_name,
                        "stock_code": stock_code,
                        "stock_name": stock_name,
                        "source": SOURCE,
                        "updated_at": "",
                        "confidence": 100,
                    }
                )
        total = int(payload.get("total") or len(members))
        if len(members) >= total or len(items) < 500:
            break
        page += 1
    return members


def save_to_sqlite(
    boards: list[dict[str, object]],
    members: list[dict[str, object]],
    *,
    db_path: Path | str = database.DB_PATH,
) -> None:
    """Write cleaned raw data into SQLite."""
    database.execute_many(
        """
        INSERT OR REPLACE INTO astock_boards
          (board_type, board_code, board_name, source, member_count, updated_at, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                str(board["board_type"]),
                str(board["board_code"]),
                str(board["board_name"]),
                str(board["source"]),
                int(board["member_count"]),
                str(board["updated_at"]),
                int(board["confidence"]),
            )
            for board in boards
        ],
        db_path,
    )
    database.execute_many(
        """
        INSERT OR REPLACE INTO astock_board_members
          (board_code, board_name, stock_code, stock_name, source, updated_at, confidence)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                str(member["board_code"]),
                str(member["board_name"]),
                str(member["stock_code"]),
                str(member["stock_name"]),
                str(member["source"]),
                str(member["updated_at"]),
                int(member["confidence"]),
            )
            for member in members
        ],
        db_path,
    )


def clean_board(
    *,
    board_type: str,
    board_code: str,
    board_name: str,
    member_count: int,
    updated_at: str,
) -> dict[str, object]:
    """Normalize one board row."""
    if board_type not in BOARD_FS:
        raise ValueError("board_type only supports industry, concept")
    return {
        "board_type": board_type,
        "board_code": board_code.strip(),
        "board_name": board_name.strip(),
        "source": SOURCE,
        "member_count": int(member_count),
        "updated_at": updated_at,
        "confidence": 100,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows([{key: row.get(key, "") for key in fieldnames} for row in rows])


def ensure_astock_schema(db_path: Path | str) -> None:
    """Add metadata columns when an older local DB already exists."""
    for table, columns in {
        "astock_boards": {
            "confidence": "INTEGER NOT NULL DEFAULT 100",
        },
        "astock_board_members": {
            "source": f"TEXT NOT NULL DEFAULT '{SOURCE}'",
            "confidence": "INTEGER NOT NULL DEFAULT 100",
        },
    }.items():
        existing = {
            row["name"]
            for row in database.fetch_all(f"PRAGMA table_info({table})", db_path=db_path)
        }
        for column, ddl in columns.items():
            if column not in existing:
                database.execute(f"ALTER TABLE {table} ADD COLUMN {column} {ddl}", db_path=db_path)


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


def em_get_json(url: str, params: dict[str, str]) -> dict[str, object]:
    """Eastmoney GET with light throttling based on a-stock-data guidance."""
    time.sleep(1.1)
    response = requests.get(
        url,
        params=params,
        timeout=20,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Referer": "https://quote.eastmoney.com/center/boardlist.html",
        },
    )
    response.raise_for_status()
    return response.json()


def _sync_board_type(
    board_type: str,
    board_fetcher: Callable[[str], list[dict[str, object]]],
    member_fetcher: Callable[[dict[str, object]], list[dict[str, object]]],
    updated_at: str,
) -> list[dict[str, object]]:
    boards = []
    seen_codes = set()
    for raw_board in board_fetcher(board_type):
        board = clean_board(
            board_type=board_type,
            board_code=str(raw_board["board_code"]),
            board_name=str(raw_board["board_name"]),
            member_count=0,
            updated_at=updated_at,
        )
        if board["board_code"] in seen_codes:
            continue
        seen_codes.add(board["board_code"])
        members = member_fetcher(board)
        for member in members:
            member["updated_at"] = updated_at
            member["source"] = member.get("source", SOURCE)
            member["confidence"] = int(member.get("confidence", 100))
        board["member_count"] = len(members)
        board["_members"] = members
        boards.append(board)
    return boards


if __name__ == "__main__":
    main()
