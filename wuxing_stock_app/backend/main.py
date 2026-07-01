"""FastAPI entrypoint for the mobile backend."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from wuxing_stock_app import database
from wuxing_stock_app.backend.api import routes_free, routes_industry, routes_paid, routes_payment, routes_user

cors_origins = [
    origin.strip()
    for origin in os.getenv("WUXING_CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
    if origin.strip()
]

app = FastAPI(
    title="五行行业动能分析 API",
    version="0.1.0",
    description="本地运行的手机端 API，负责五行时间、行业分析、权限校验和报告数据输出。",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    """Initialize local SQLite tables before serving API requests."""
    database.initialize_database()


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.exception_handler(StarletteHTTPException)
def http_exception_handler(request, exc: StarletteHTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "code": "HTTP_ERROR",
            "message": str(exc.detail),
            "data": None,
            "paywall": None,
            "risk_notice": "Observation only. Not investment advice.",
        },
    )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc: RequestValidationError) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "code": "VALIDATION_ERROR",
            "message": "invalid request",
            "data": {"errors": exc.errors()},
            "paywall": None,
            "risk_notice": "Observation only. Not investment advice.",
        },
    )


app.include_router(routes_free.router, prefix="/api/free", tags=["free"])
app.include_router(routes_industry.router, prefix="/api/industry", tags=["industry"])
app.include_router(routes_paid.router, prefix="/api/paid", tags=["paid"])
app.include_router(routes_payment.router, prefix="/api/payment", tags=["payment"])
app.include_router(routes_user.router, prefix="/api/user", tags=["user"])
