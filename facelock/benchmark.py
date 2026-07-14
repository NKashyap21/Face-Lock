import time
import logging

class BenchmarkTimer:
    """
    A reusable context manager for timing block execution and logging the results.
    """
    def __init__(self, name: str, logger: logging.Logger = None):
        self.name = name
        self.logger = logger or logging.getLogger(__name__)
        self.start_time = None
        self.elapsed = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.elapsed = time.perf_counter() - self.start_time
        self.logger.info(f"{self.name} completed in {self.elapsed:.3f} seconds")
