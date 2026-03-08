import httpx
from src.core.config import MANGADEX_API_URL, MAX_RETRIES, RETRY_BACKOFF_FACTOR
from src.core.rate_limiter import RateLimiter
import asyncio
import logging

class MangaDexClient:
    def __init__(self, concurrent_limit: int = 5):
        self.client = httpx.AsyncClient(
            base_url=MANGADEX_API_URL,
            timeout=30.0,
            headers={"User-Agent": "MDex-Singularity/4.0 (2026 Audited)"}
        )
        self.limiter = RateLimiter(concurrent_limit)

    async def get(self, endpoint: str, params: dict = None):
        """Perform an async GET request with rate limiting and retry logic."""
        for attempt in range(MAX_RETRIES):
            async with self.limiter:
                try:
                    response = await self.client.get(endpoint, params=params)
                    if response.status_code == 429:  # Rate limited
                        retry_after = int(response.headers.get("Retry-After", 5))
                        await asyncio.sleep(retry_after)
                        continue

                    response.raise_for_status()
                    return response.json()
                except httpx.HTTPStatusError as e:
                    if e.response.status_code >= 500:
                        await asyncio.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                        continue
                    raise  # pragma: no cover
                except (httpx.RequestError, asyncio.TimeoutError):
                    await asyncio.sleep(RETRY_BACKOFF_FACTOR ** attempt)
                    continue

        raise Exception(f"Max retries exceeded for {endpoint}")

    async def check_health(self) -> bool:
        """Check if MangaDex API is reachable."""
        try:
            # We don't use self.get here to avoid retry logic for a simple health check
            response = await self.client.get("/manga", params={"limit": 1})
            return response.status_code == 200
        except Exception:
            return False

    async def close(self):
        await self.client.aclose()
