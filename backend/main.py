import sys
import time
from fastapi import FastAPI, Request, Response, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from loguru import logger

from config import settings
from api.health import router as health_router
from api.upload import router as upload_router
from api.chat import router as chat_router
from utils.exceptions import AppBaseException

# Initialize production-grade FastAPI application context
app = FastAPI(
    title="Intelligent LMS Backend Subsystem",
    description="Production-grade AI Multi-Agent core driving RAG, Assessment, and Analytics.",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# ------------------------------------------------------------------------------
# CORS MIDDLEWARE SETUP
# ------------------------------------------------------------------------------
logger.info(f"[MAIN] Registering CORS policy. Allowed Origins: {settings.ALLOWED_ORIGINS}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------------------------------------------------
# GLOBAL HTTP TELEMETRY MIDDLEWARE
# ------------------------------------------------------------------------------
@app.middleware("http")
async def log_request_lifecycle(request: Request, call_next) -> Response:
    """
    Interceptors for incoming HTTP calls. Calculates and tracks operational 
    latencies, paths, method verifications, and outputs extensive diagnostic traces.
    """
    start_time = time.perf_counter()
    method = request.method
    path = request.url.path
    
    logger.info(f"[MAIN] [HTTP INBOUND] HTTP {method} -> '{path}' incoming.")
    
    try:
        response: Response = await call_next(request)
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        
        # Color-code status logs based on severity thresholds
        if response.status_code >= 400:
            logger.error(
                f"[MAIN] [HTTP OUTBOUND] HTTP {method} -> '{path}' failed with "
                f"Status: {response.status_code} | Latency: {duration_ms}ms"
            )
        else:
            logger.info(
                f"[MAIN] [HTTP OUTBOUND] HTTP {method} -> '{path}' processed successfully. "
                f"Status: {response.status_code} | Latency: {duration_ms}ms"
            )
        return response
    except Exception as e:
        duration_ms = int((time.perf_counter() - start_time) * 1000)
        logger.exception(
            f"[MAIN] [HTTP CRASH] Internal crash during request parsing on "
            f"HTTP {method} -> '{path}' | Latency: {duration_ms}ms"
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "message": "A critical, unhandled server execution exception occurred.",
                "timestamp": "2026-07-03T20:55:14Z",
                "metadata": {"error_type": type(e).__name__}
            }
        )

# ------------------------------------------------------------------------------
# EXCEPTION HANDLERS
# ------------------------------------------------------------------------------
@app.exception_handler(AppBaseException)
async def custom_app_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    """
    Transforms custom domain exceptions down the stack directly into standardized 
    JSON response payloads matching Frontend interface specifications.
    """
    logger.error(
        f"[MAIN] [EXCEPTION INTERCEPT] Domain Exception: {type(exc).__name__} | "
        f"Message: {exc.message} | HTTP Status: {exc.status_code}"
    )
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.message,
            "timestamp": "2026-07-03T20:55:14Z",
            "metadata": exc.details
        }
    )

# ------------------------------------------------------------------------------
# ROUTER REGISTRATION
# ------------------------------------------------------------------------------
logger.info("[MAIN] Mounting operational presentation API router blocks.")
app.include_router(health_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(chat_router, prefix="/api")

logger.info("[MAIN] Intelligent LMS API server successfully configured and pre-warmed.")