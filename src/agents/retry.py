"""
Jeeves ADHD Butler — Retry med Exponential Backoff
===================================================
Dekorator för att hantera tillfälliga nätverks-/API-fel.
Baserad på error-handling-patterns ADVANCED.md.
"""
import time
import logging
from functools import wraps
from typing import TypeVar, Callable

logger = logging.getLogger(__name__)

T = TypeVar('T')


def retry(
    max_attempts: int = 3,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_name: str = "Retry"
):
    """
    Retry-dekorator med exponential backoff.
    
    Användning:
        @retry(max_attempts=3, exceptions=(ConnectionError, TimeoutError))
        def risky_operation():
            ...
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts - 1:
                        sleep_time = backoff_factor ** attempt
                        logger.warning(
                            f"[{logger_name}] Försök {attempt + 1}/{max_attempts} "
                            f"misslyckades för {func.__name__}: {e}. "
                            f"Väntar {sleep_time:.1f}s..."
                        )
                        time.sleep(sleep_time)
                        continue
                    logger.error(
                        f"[{logger_name}] Alla {max_attempts} försök "
                        f"misslyckades för {func.__name__}: {e}"
                    )
                    raise
            raise last_exception  # Säkerhetsnät
        return wrapper
    return decorator


def with_fallback(
    primary: Callable[..., T],
    fallback: Callable[..., T],
    log_error: bool = True,
    logger_name: str = "Fallback"
) -> T:
    """
    Kör primary-funktionen; om den misslyckas, kör fallback.
    
    Användning:
        result = with_fallback(
            primary=lambda: api.get_data(),
            fallback=lambda: cache.get_data()
        )
    """
    try:
        return primary()
    except Exception as e:
        if log_error:
            logger.warning(
                f"[{logger_name}] Primär funktion misslyckades: {e}. "
                f"Använder fallback."
            )
        return fallback()
