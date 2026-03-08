import asyncio

class RateLimiter:
    """Simple async semaphore wrapper for API rate limiting."""
    def __init__(self, concurrent_limit: int):
        self.semaphore = asyncio.Semaphore(concurrent_limit)

    async def __aenter__(self):
        await self.semaphore.acquire()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()
