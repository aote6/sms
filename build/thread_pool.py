"""WorkerPool - 线程池"""

from concurrent.futures import ThreadPoolExecutor, wait


class WorkerPool:
    def __init__(self, workers: int = 4):
        self.pool = ThreadPoolExecutor(max_workers=workers)

    def submit(self, fn, *args):
        return self.pool.submit(fn, *args)

    def wait(self, futures):
        return wait(futures)

    def shutdown(self):
        self.pool.shutdown(wait=True)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
