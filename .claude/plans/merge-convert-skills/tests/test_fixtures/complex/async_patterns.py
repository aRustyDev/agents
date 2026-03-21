"""Async/await patterns for testing effect extraction."""

import asyncio
from collections.abc import AsyncIterator, Coroutine


async def fetch_data(url: str) -> str:
    """Simulate fetching data from a URL."""
    await asyncio.sleep(0.01)  # Simulate network delay
    return f"Data from {url}"


async def process_urls(urls: list[str]) -> list[str]:
    """Process multiple URLs concurrently."""
    tasks = [fetch_data(url) for url in urls]
    return await asyncio.gather(*tasks)


async def stream_numbers(count: int) -> AsyncIterator[int]:
    """Stream numbers asynchronously."""
    for i in range(count):
        await asyncio.sleep(0.001)
        yield i


async def timeout_wrapper(
    coro: Coroutine,
    timeout: float,
) -> str:
    """Wrap a coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except TimeoutError:
        return "timeout"


async def retry_async(
    coro_factory,
    max_attempts: int = 3,
) -> str:
    """Retry an async operation multiple times."""
    last_error = None
    for attempt in range(max_attempts):
        try:
            return await coro_factory()
        except Exception as e:
            last_error = e
            await asyncio.sleep(0.01 * (2 ** attempt))
    raise RuntimeError(f"Failed after {max_attempts} attempts") from last_error
