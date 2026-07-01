# 五行股票行业分析软件

本目录是当前项目内的模块化应用骨架，不是独立的新项目。

设计原则：

- UI 页面只负责展示和交互。
- 业务逻辑放在 `modules/`。
- 数据统一通过 `database.py` 读写。
- 配置数据放在 `data/`。
- 报告模板放在 `templates/`。
- 核心模块都有对应测试文件。

当前状态：

- 已创建项目骨架。
- 已提供占位函数。
- 暂未实现复杂业务逻辑。

运行方式：

```bash
python wuxing_stock_app/app.py
python -m unittest discover -s wuxing_stock_app/tests
```

## FastAPI backend

Windows PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\start_backend.ps1
powershell -ExecutionPolicy Bypass -File scripts\stop_backend.ps1
python scripts\smoke_test.py --base-url http://127.0.0.1:8000
```

Manual start:

```powershell
python -m uvicorn wuxing_stock_app.backend.main:app --host 127.0.0.1 --port 8000
```

Local URLs:

```text
http://127.0.0.1:8000/api/health
http://127.0.0.1:8000/docs
```
