# Mobile

Next.js mobile H5 / PWA frontend.

## Run

```powershell
cd "C:\Users\Administrator\Documents\五行股票行业分析软件"
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
powershell -ExecutionPolicy Bypass -File scripts\start_mobile.ps1
```

## Stop

```powershell
powershell -ExecutionPolicy Bypass -File scripts\stop_mobile.ps1
powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
```

## Verify

```powershell
python scripts\smoke_test.py --base-url http://127.0.0.1:8000
node scripts\check_mobile_pages.js
cd mobile
npm.cmd run build
```

## URLs

```text
Backend: http://127.0.0.1:8000
Mobile:  http://127.0.0.1:3000
```
