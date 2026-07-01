"""P0 smoke test for FastAPI endpoints."""

from __future__ import annotations

import json
import sys
import argparse
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
from fastapi.testclient import TestClient

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from wuxing_stock_app.backend.main import app
from wuxing_stock_app import database
from wuxing_stock_app.modules.auth_engine import create_unlock_code


DATE_TEXT = "2026-06-29"
REPORT_PATH = Path("smoke_test_report.md")
REQUIRED_KEYS = {"success", "code", "message", "data", "paywall", "risk_notice"}


class HttpClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")

    def get(self, path: str, params: dict[str, Any] | None = None):
        return requests.get(f"{self.base_url}{path}", params=params, timeout=20)

    def post(self, path: str, json: dict[str, Any] | None = None):
        return requests.post(f"{self.base_url}{path}", json=json, timeout=20)

    def request(self, method: str, path: str, json: dict[str, Any] | None = None):
        return requests.request(method, f"{self.base_url}{path}", json=json, timeout=20)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="")
    args = parser.parse_args()
    client = HttpClient(args.base_url) if args.base_url else TestClient(app)
    results: list[dict[str, Any]] = []

    category_id = _first_category(client, results)
    subcategory_id = _first_subcategory_id()

    _check(client, "GET /api/health", "GET", "/api/health", results, expect_envelope=False)
    _check_with_usage(client, "GET /api/free/year", "GET", f"/api/free/year?date={DATE_TEXT}", "/api/free/year", results)
    _check_with_usage(client, "GET /api/free/week", "GET", f"/api/free/week?date={DATE_TEXT}", "/api/free/week", results)
    _check(client, "GET /api/free/period month", "GET", f"/api/free/period?period_type=month&date={DATE_TEXT}", results)
    _check(client, "GET /api/free/period day", "GET", f"/api/free/period?period_type=day&date={DATE_TEXT}", results)
    _check_with_usage(client, "GET /api/free/categories", "GET", "/api/free/categories", "/api/free/categories", results)
    _check_with_usage(client, "GET /api/free/category/{category_id}", "GET", f"/api/free/category/{category_id}", "/api/free/category", results)
    _check(client, "GET /api/industry/subcategories", "GET", "/api/industry/subcategories", results)
    _check(client, "GET /api/industry/astock-boards", "GET", "/api/industry/astock-boards", results)

    _check(
        client,
        "POST /api/paid/subcategory locked",
        "POST",
        "/api/paid/subcategory",
        results,
        json_body={"subcategory_id": subcategory_id, "date": DATE_TEXT, "user_id": "smoke", "unlock_code": "BAD"},
        expected_code="PAYWALL_REQUIRED",
    )

    sub_code = create_unlock_code("PAID_SUBCATEGORY_SINGLE", subcategory_id, max_use_count=3)["code"]
    paid_sub_reports_before = _report_count("smoke")
    paid_sub_logs_before = _usage_count("/api/paid/subcategory")
    _check(
        client,
        "POST /api/paid/subcategory unlocked",
        "POST",
        "/api/paid/subcategory",
        results,
        json_body={"subcategory_id": subcategory_id, "date": DATE_TEXT, "user_id": "smoke", "unlock_code": sub_code},
        expected_code="OK",
    )
    paid_sub_reports_after = _report_count("smoke")
    paid_sub_logs_after = _usage_count("/api/paid/subcategory")
    results.append(
        {
            "name": "paid_subcategory persistence",
            "passed": paid_sub_reports_after > paid_sub_reports_before and paid_sub_logs_after > paid_sub_logs_before,
            "details": f"reports={paid_sub_reports_before}->{paid_sub_reports_after}; logs={paid_sub_logs_before}->{paid_sub_logs_after}",
        }
    )

    _check(
        client,
        "POST /api/paid/ranking locked",
        "POST",
        "/api/paid/ranking",
        results,
        json_body={"period_type": "week", "ranking_type": "favorable", "date": DATE_TEXT, "user_id": "smoke", "unlock_code": "BAD"},
        expected_code="PAYWALL_REQUIRED",
    )

    ranking_target = f"week:favorable:{DATE_TEXT}"
    ranking_code = create_unlock_code("PAID_WEEK_RANKING", ranking_target, max_use_count=3)["code"]
    rank_reports_before = _report_count("smoke")
    rank_logs_before = _usage_count("/api/paid/ranking")
    _check(
        client,
        "POST /api/paid/ranking unlocked",
        "POST",
        "/api/paid/ranking",
        results,
        json_body={"period_type": "week", "ranking_type": "favorable", "date": DATE_TEXT, "user_id": "smoke", "unlock_code": ranking_code},
        expected_code="OK",
        item_count=5,
    )
    rank_reports_after = _report_count("smoke")
    rank_logs_after = _usage_count("/api/paid/ranking")
    results.append(
        {
            "name": "paid_ranking persistence",
            "passed": rank_reports_after > rank_reports_before and rank_logs_after > rank_logs_before,
            "details": f"reports={rank_reports_before}->{rank_reports_after}; logs={rank_logs_before}->{rank_logs_after}",
        }
    )

    mock_target = "tech_semiconductor"
    order_response = client.post(
        "/api/payment/create_mock_order",
        json={
            "access_type": "PAID_SUBCATEGORY_SINGLE",
            "target_key": mock_target,
            "amount": 990,
            "payment_channel": "WECHAT",
            "max_use_count": 1,
        },
    )
    order_payload = order_response.json()
    order_log_count = _usage_count("/api/payment/create_mock_order")
    order_ok = (
        order_response.status_code == 200
        and order_payload.get("code") == "OK"
        and bool(order_payload.get("data", {}).get("unlock_code", {}).get("code"))
        and order_log_count > 0
    )
    results.append(
        {
            "name": "POST /api/payment/create_mock_order",
            "passed": order_ok,
            "details": f"status={order_response.status_code}; code={order_payload.get('code')}; logs={order_log_count}",
        }
    )

    payment_code = order_payload.get("data", {}).get("unlock_code", {}).get("code", "")
    verify_log_before = _usage_count("/api/payment/verify_unlock_code")
    _check(
        client,
        "POST /api/payment/verify_unlock_code",
        "POST",
        "/api/payment/verify_unlock_code",
        results,
        json_body={
            "access_type": "PAID_SUBCATEGORY_SINGLE",
            "target_key": mock_target,
            "unlock_code": payment_code,
        },
        expected_code="OK",
    )
    verify_log_after = _usage_count("/api/payment/verify_unlock_code")
    results.append(
        {
            "name": "usage_logs payment verify",
            "passed": verify_log_after > verify_log_before,
            "details": f"logs={verify_log_before}->{verify_log_after}",
        }
    )

    history_user = "smoke_history"
    history_code = create_unlock_code("PAID_SUBCATEGORY_SINGLE", subcategory_id, max_use_count=1)["code"]
    client.post(
        "/api/paid/subcategory",
        json={
            "subcategory_id": subcategory_id,
            "date": DATE_TEXT,
            "user_id": history_user,
            "unlock_code": history_code,
        },
    )
    history_logs_before = _usage_count("/api/user/reports")
    history_response = client.get("/api/user/reports", params={"user_id": history_user})
    history_logs_after = _usage_count("/api/user/reports")
    history_payload = history_response.json()
    history_items = history_payload.get("data", {}).get("items", [])
    history_ok = (
        history_response.status_code == 200
        and history_payload.get("code") == "OK"
        and len(history_items) >= 1
        and history_logs_after > history_logs_before
    )
    results.append(
        {
            "name": "GET /api/user/reports",
            "passed": history_ok,
            "details": f"status={history_response.status_code}; count={len(history_items)}; logs={history_logs_before}->{history_logs_after}",
        }
    )

    report_id = history_items[0]["id"] if history_items else 0
    detail_logs_before = _usage_count("/api/user/report")
    detail_response = client.get(f"/api/user/report/{report_id}", params={"user_id": history_user})
    detail_logs_after = _usage_count("/api/user/report")
    detail_payload = detail_response.json()
    detail_ok = (
        detail_response.status_code == 200
        and detail_payload.get("code") == "OK"
        and bool(detail_payload.get("data", {}).get("payload"))
        and detail_logs_after > detail_logs_before
    )
    results.append(
        {
            "name": "GET /api/user/report/{report_id}",
            "passed": detail_ok,
            "details": f"status={detail_response.status_code}; code={detail_payload.get('code')}; logs={detail_logs_before}->{detail_logs_after}",
        }
    )

    _write_report(results)


def _check(
    client: TestClient,
    name: str,
    method: str,
    path: str,
    results: list[dict[str, Any]],
    *,
    json_body: dict[str, Any] | None = None,
    expect_envelope: bool = True,
    expected_code: str | None = None,
    item_count: int | None = None,
) -> None:
    response = client.request(method, path, json=json_body)
    passed = response.status_code == 200
    details: list[str] = [f"status={response.status_code}"]
    payload: dict[str, Any] = {}

    try:
        payload = response.json()
    except json.JSONDecodeError:
        passed = False
        details.append("invalid_json")

    if expect_envelope:
        missing = sorted(REQUIRED_KEYS - set(payload))
        if missing:
            passed = False
            details.append(f"missing={missing}")
    if expected_code and payload.get("code") != expected_code:
        passed = False
        details.append(f"code={payload.get('code')}")
    if item_count is not None:
        count = len(payload.get("data", {}).get("items", []))
        if count != item_count:
            passed = False
            details.append(f"items={count}")

    results.append({"name": name, "passed": passed, "details": "; ".join(details)})


def _check_with_usage(
    client: TestClient,
    name: str,
    method: str,
    path: str,
    endpoint: str,
    results: list[dict[str, Any]],
) -> None:
    before = _usage_count(endpoint)
    _check(client, name, method, path, results)
    after = _usage_count(endpoint)
    usage_passed = after > before
    results.append({"name": f"usage_logs {endpoint}", "passed": usage_passed, "details": f"logs={before}->{after}"})


def _first_category(client: TestClient, results: list[dict[str, Any]]) -> str:
    response = client.get("/api/free/categories")
    items = response.json().get("data", {}).get("items", [])
    if not items:
        results.append({"name": "load first category", "passed": False, "details": "no categories"})
        raise SystemExit(1)
    return items[0]["category_id"]


def _first_subcategory_id() -> str:
    data_path = Path("wuxing_stock_app/data/industry_subcategories.json")
    items = json.loads(data_path.read_text(encoding="utf-8"))
    if not items:
        raise SystemExit("no subcategories")
    return items[0]["subcategory_id"]


def _write_report(results: list[dict[str, Any]]) -> None:
    passed = sum(1 for item in results if item["passed"])
    lines = [
        "# Smoke Test Report",
        "",
        f"- generated_at: {datetime.now().isoformat(timespec='seconds')}",
        f"- result: {passed}/{len(results)} passed",
        "",
        "| Item | Result | Details |",
        "| --- | --- | --- |",
    ]
    for item in results:
        status = "PASS" if item["passed"] else "FAIL"
        lines.append(f"| {item['name']} | {status} | {item['details']} |")
    REPORT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"smoke test: {passed}/{len(results)} passed")
    print(f"report: {REPORT_PATH}")


def _usage_count(endpoint: str) -> int:
    database.initialize_database()
    row = database.fetch_one("SELECT count(*) AS count FROM usage_logs WHERE endpoint = ?", (endpoint,))
    return int(row["count"]) if row else 0


def _report_count(user_id: str) -> int:
    database.initialize_database()
    row = database.fetch_one("SELECT count(*) AS count FROM reports WHERE user_id = ?", (user_id,))
    return int(row["count"]) if row else 0


if __name__ == "__main__":
    main()
