import time
from typing import Callable, Any

def time_it(func: Callable) -> Callable:
    """A decorator to log the execution time of a function."""
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"Function {func.__name__} took {end_time - start_time:.4f} seconds to execute.")
        return result
    return wrapper
