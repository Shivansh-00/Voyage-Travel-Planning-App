from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.config import get_settings
from app.core.logging import configure_logging
from app.core.middleware import RequestLoggingMiddleware
from app.dependencies import get_travel_service
from app.schemas.travel import TravelRequest, TravelResponse
from app.services.travel_service import TravelService

configure_logging()
settings = get_settings()
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/health')
async def health_check() -> dict[str, str]:
    return {'status': 'ok', 'service': settings.app_name}


@app.post(f'{settings.api_prefix}/plan', response_model=TravelResponse)
@limiter.limit(settings.rate_limit)
async def create_plan(
    request: Request,
    payload: TravelRequest,
    travel_service: TravelService = Depends(get_travel_service),
) -> TravelResponse:
    _ = request
    return await travel_service.plan(payload)
