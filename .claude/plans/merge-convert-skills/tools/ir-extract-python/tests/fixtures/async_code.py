"""Async code fixture for testing async pattern extraction."""

from typing import AsyncIterator


async def fetch_data(url: str) -> bytes:
    """Fetch data from a URL asynchronously.

    Args:
        url: The URL to fetch.

    Returns:
        The response data as bytes.
    """
    # Simulated async HTTP call
    await some_async_http_call(url)
    return b"data"


async def process_stream(items: AsyncIterator[int]) -> int:
    """Process items from an async stream.

    Args:
        items: Async iterator of integers.

    Returns:
        Sum of all items.
    """
    total = 0
    async for item in items:
        total += item
    return total


async def batch_process(urls: list[str]) -> list[bytes]:
    """Process multiple URLs in parallel.

    Args:
        urls: List of URLs to fetch.

    Returns:
        List of response data.
    """
    results = []
    for url in urls:
        data = await fetch_data(url)
        results.append(data)
    return results


async def async_generator(n: int) -> AsyncIterator[int]:
    """Generate integers asynchronously.

    Args:
        n: Number of integers to generate.

    Yields:
        Integers from 0 to n-1.
    """
    for i in range(n):
        yield i


async def async_context_manager_example() -> None:
    """Example using async context managers."""
    async with some_async_resource() as resource:
        await resource.do_something()
