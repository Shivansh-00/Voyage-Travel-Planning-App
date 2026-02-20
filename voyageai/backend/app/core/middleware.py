from time import perf_counter
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.core.logging import get_logger


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        logger = get_logger('request')
        start = perf_counter()
        response: Response = await call_next(request)
        duration_ms = round((perf_counter() - start) * 1000, 2)
        logger.info(
            'request_complete',
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=duration_ms,
        )
        response.headers['X-Process-Time'] = str(duration_ms)
        return response
