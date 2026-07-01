# 五行股票行业分析软件

## Quick Start

```powershell
cd "C:\Users\Administrator\Documents\五行股票行业分析软件"
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
powershell -ExecutionPolicy Bypass -File scripts\start_mobile.ps1
```

## URLs

```text
Backend API: http://127.0.0.1:8000/docs
Mobile H5:   http://127.0.0.1:3000
```

## Verify

```powershell
python scripts\smoke_test.py --base-url http://127.0.0.1:8000
node scripts\check_mobile_pages.js
cd mobile
npm.cmd run build
```

All-in-one:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\verify_all.ps1
```

Production preview:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_mobile_prod.ps1
```

## Server Preview

Copy `deploy.env.example` to your server environment and adjust:

```powershell
$env:WUXING_CORS_ORIGINS="http://your-domain-or-ip:3000"
$env:NEXT_PUBLIC_API_BASE="http://your-domain-or-ip:8000"
powershell -ExecutionPolicy Bypass -File scripts\start_backend_public.ps1
powershell -ExecutionPolicy Bypass -File scripts\start_mobile_public.ps1
```

Open:

```text
Backend: http://your-domain-or-ip:8000/api/health
Mobile:  http://your-domain-or-ip:3000
```

## Stop

```powershell
powershell -ExecutionPolicy Bypass -File scripts\stop_mobile.ps1
powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
```
