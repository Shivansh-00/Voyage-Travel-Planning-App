from functools import lru_cache
from app.config import get_settings
from app.memory.cache import RedisCache
from app.services.travel_service import TravelService


@lru_cache(maxsize=1)
def get_cache() -> RedisCache:
    settings = get_settings()
    return RedisCache(settings.redis_url)


def get_travel_service() -> TravelService:
    """Create a fresh TravelService each request (graph is lightweight)."""
    return TravelService(get_cache())
