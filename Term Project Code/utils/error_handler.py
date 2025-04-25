import functools
import logging
from typing import Callable, Any, Type, Union, Tuple
from typing import Optional
import traceback
import asyncio

logger = logging.getLogger(__name__)

class ResearchAssistantError(Exception):
    """Base exception class for research assistant errors."""
    pass

def handle_errors(
    error_types: Union[Type[Exception], Tuple[Type[Exception], ...]] = Exception,
    logger: Optional[logging.Logger] = None,
    return_value: Any = None
) -> Callable:
    """Decorator for handling exceptions."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            try:
                return await func(*args, **kwargs)
            except error_types as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                return return_value
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except error_types as e:
                if logger:
                    logger.error(f"Error in {func.__name__}: {str(e)}\n{traceback.format_exc()}")
                return return_value
        
        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator