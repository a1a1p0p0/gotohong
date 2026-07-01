# Smoke Test Report

- generated_at: 2026-07-01T12:20:19
- result: 24/24 passed

| Item | Result | Details |
| --- | --- | --- |
| GET /api/health | PASS | status=200 |
| GET /api/free/year | PASS | status=200 |
| usage_logs /api/free/year | PASS | logs=137->138 |
| GET /api/free/week | PASS | status=200 |
| usage_logs /api/free/week | PASS | logs=171->172 |
| GET /api/free/period month | PASS | status=200 |
| GET /api/free/period day | PASS | status=200 |
| GET /api/free/categories | PASS | status=200 |
| usage_logs /api/free/categories | PASS | logs=173->174 |
| GET /api/free/category/{category_id} | PASS | status=200 |
| usage_logs /api/free/category | PASS | logs=73->74 |
| GET /api/industry/subcategories | PASS | status=200 |
| GET /api/industry/astock-boards | PASS | status=200 |
| POST /api/paid/subcategory locked | PASS | status=200 |
| POST /api/paid/subcategory unlocked | PASS | status=200 |
| paid_subcategory persistence | PASS | reports=140->141; logs=229->230 |
| POST /api/paid/ranking locked | PASS | status=200 |
| POST /api/paid/ranking unlocked | PASS | status=200 |
| paid_ranking persistence | PASS | reports=141->142; logs=226->227 |
| POST /api/payment/create_mock_order | PASS | status=200; code=OK; logs=82 |
| POST /api/payment/verify_unlock_code | PASS | status=200 |
| usage_logs payment verify | PASS | logs=58->59 |
| GET /api/user/reports | PASS | status=200; count=20; logs=79->80 |
| GET /api/user/report/{report_id} | PASS | status=200; code=OK; logs=64->65 |
