# Backend API

Base URL:

```text
http://127.0.0.1:8000
```

## Free

```text
GET /api/health
GET /api/free/year?date=2026-06-29
GET /api/free/week?date=2026-06-29
GET /api/free/categories
GET /api/free/category/{category_id}
```

## Paid

```text
POST /api/paid/day
POST /api/paid/subcategory
POST /api/paid/ranking
```

Locked response:

```json
{
  "success": false,
  "code": "PAYWALL_REQUIRED",
  "message": "...",
  "data": null,
  "paywall": {
    "required": true,
    "next_action": "verify_unlock_code"
  }
}
```

## Payment

```text
POST /api/payment/create_mock_order
POST /api/payment/verify_unlock_code
```

## User

```text
GET /api/user/reports?user_id={user_id}
GET /api/user/report/{report_id}?user_id={user_id}
```

## Smoke Test

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
python scripts\smoke_test.py --base-url http://127.0.0.1:8000
```
