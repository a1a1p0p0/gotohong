"""数据库访问层。

所有模块通过本文件读写 SQLite，避免业务模块直接操作数据库连接。
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any


BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "reports" / "wuxing_stock_app.db"
SCHEMA_PATH = BASE_DIR / "schema.sql"


def get_connection(db_path: Path | str = DB_PATH) -> sqlite3.Connection:
    """创建 SQLite 连接。"""
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(path)


def initialize_database(db_path: Path | str = DB_PATH) -> None:
    """初始化数据库结构。"""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
        conn.commit()
    finally:
        conn.close()


def execute(
    sql: str,
    params: tuple[Any, ...] = (),
    db_path: Path | str = DB_PATH,
) -> None:
    """执行写入语句。"""
    conn = get_connection(db_path)
    try:
        conn.execute(sql, params)
        conn.commit()
    finally:
        conn.close()


def execute_many(
    sql: str,
    params_list: list[tuple[Any, ...]],
    db_path: Path | str = DB_PATH,
) -> None:
    """批量执行写入语句。"""
    conn = get_connection(db_path)
    try:
        conn.executemany(sql, params_list)
        conn.commit()
    finally:
        conn.close()


def fetch_one(
    sql: str,
    params: tuple[Any, ...] = (),
    db_path: Path | str = DB_PATH,
) -> dict[str, Any] | None:
    """读取单行数据。"""
    conn = get_connection(db_path)
    try:
        conn.row_factory = sqlite3.Row
        row = conn.execute(sql, params).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def fetch_all(
    sql: str,
    params: tuple[Any, ...] = (),
    db_path: Path | str = DB_PATH,
) -> list[dict[str, Any]]:
    """读取多行数据。"""
    conn = get_connection(db_path)
    try:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def set_meta(key: str, value: str, db_path: Path | str = DB_PATH) -> None:
    """保存简单配置。"""
    initialize_database(db_path)
    execute(
        "INSERT OR REPLACE INTO app_meta (key, value) VALUES (?, ?)",
        (key, value),
        db_path,
    )


def get_meta(key: str, db_path: Path | str = DB_PATH) -> str | None:
    """读取简单配置。"""
    initialize_database(db_path)
    row = fetch_one("SELECT value FROM app_meta WHERE key = ?", (key,), db_path)
    return row["value"] if row else None
