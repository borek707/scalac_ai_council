from __future__ import annotations

import asyncio
import functools
import logging
import random
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


class RetryConfig:
    """Configuration for retry behavior."""

    max_retries: int = 3
    base_delay: float = 1.0
    max_delay: float = 60.0
    exceptions: tuple[type[Exception], ...] = (Exception,)
    non_retryable_exceptions: tuple[type[Exception], ...] = ()

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exceptions: tuple[type[Exception], ...] | None = None,
        non_retryable_exceptions: tuple[type[Exception], ...] | None = None,
    ) -> None:
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay
        if exceptions is not None:
            self.exceptions = exceptions
        if non_retryable_exceptions is not None:
            self.non_retryable_exceptions = non_retryable_exceptions


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    non_retryable_exceptions: tuple[type[Exception], ...] = (),
) -> Callable[[F], F]:
    """Decorator that retries an async function with exponential backoff and jitter.

    Retries on specified exceptions with a delay that doubles each attempt,
    plus a small random jitter to avoid thundering herd.

    Exceptions listed in *non_retryable_exceptions* are re-raised immediately
    without any retry, even when they are also matched by *exceptions*.  Use
    this to fast-fail on deterministic errors such as authentication failures,
    invalid model names, or bad-request (4xx) responses.
    """

    def decorator(func: F) -> F:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            config = RetryConfig(
                max_retries=max_retries,
                base_delay=base_delay,
                max_delay=max_delay,
                exceptions=exceptions,
                non_retryable_exceptions=non_retryable_exceptions,
            )
            last_exception: Exception | None = None

            for attempt in range(1, config.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except config.exceptions as exc:
                    # Fast-fail on deterministic errors that should never be retried.
                    if config.non_retryable_exceptions and isinstance(
                        exc, config.non_retryable_exceptions
                    ):
                        logger.warning(
                            "Non-retryable error in %s (not retrying): %s",
                            func.__name__,
                            exc,
                        )
                        raise

                    last_exception = exc
                    if attempt >= config.max_retries:
                        logger.warning(
                            "Function %s failed after %d attempts: %s",
                            func.__name__,
                            attempt,
                            exc,
                        )
                        break
                    delay = min(
                        config.base_delay * (2 ** (attempt - 1)), config.max_delay
                    )
                    jitter = random.uniform(0, delay * 0.1)
                    sleep_time = delay + jitter
                    logger.debug(
                        "Retry %d/%d for %s in %.2fs: %s",
                        attempt,
                        config.max_retries,
                        func.__name__,
                        sleep_time,
                        exc,
                    )
                    await asyncio.sleep(sleep_time)

            if last_exception is not None:
                raise last_exception
            return None  # pragma: no cover

        return wrapper  # type: ignore[return-value]

    return decorator
